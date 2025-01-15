---
title: "[[UI框架]]"
type: Permanent
status: done
Creation Date: 2024-05-30 18:33
tags:
---
在 studio 中使用了代码生成 UI 预制体的方式来切换和控制 UI 界面，以下是我整理的 studio 中的 UI 框架
首先是一个接口 IPanel，定义了 UI 界面的一些基本操作，同时定义了 UI 界面的数据类 IUIData
```csharp
    /// <summary>
    /// 定义Panel
    /// </summary>
    public interface IPanel
    {
        /// <summary>
        /// UI本身的节点
        /// </summary>
        Transform Transform { get; }

        /// <summary>
        /// 信息
        /// </summary>
        PanelInfo Info { get; set; }

        /// <summary>
        /// 状态
        /// </summary>
        PanelState State { get; set; }

        /// <summary>
        ///  初始化
        /// </summary>
        /// <param name="panelSearchKeys"></param>
        void Init(PanelSearchKeys panelSearchKeys);

        /// <summary>
        /// 开启Panel
        /// </summary>
        /// <param name="uiData">开启数据</param>
        void Open(IUIData uiData = null);

        /// <summary>
        /// 显示Panel
        /// </summary>
        void Display();

        /// <summary>
        /// 隐藏Panel
        /// </summary>
        void Hide();

        /// <summary>
        /// 关闭Panel
        /// </summary>
        /// <param name="destroy">是否销毁</param>
        void Close(bool destroy = true);

        /// <summary>
        /// 设置配置
        /// </summary>
        /// <param name="config"></param>
        void SetConfig(UIConfig config);

        bool UseOriginRectTrans();
    }
    /// <summary>
    /// 每个IPanel对应的Data
    /// </summary>
    public interface IUIData
    {

    }
```
UI 预制体该从什么路径加载？生成的 UI 之间的遮挡关系是如何确定的呢？UI 界面可以生成多个还是只能生成一个？这些具体的问题存在于 PanelInfo 中
```csharp
/// <summary>
    /// 保存IPanel的数据类
    /// </summary>
    public class PanelInfo
    {
        /// <summary>
        /// UIPanel的类型
        /// </summary>
        public Type PanelType;

        /// <summary>
        /// UIPanel预制加载路径
        /// </summary>
        public string Path;

        /// <summary>
        /// UIPanel名字
        /// </summary>
        public string Name;

        /// <summary>
        /// 是否加入UI的储存队列
        /// </summary>
        public bool isRecord;

        /// <summary>
        /// 是否UI层级显示在最上层
        /// </summary>
        public bool isUseOverlay;

        /// <summary>
        /// 记录UI前一个UIPanel
        /// </summary>
        public IPanel prevIPanel { get; set; }

        /// <summary>
        /// 记录UI下一个UIPanel
        /// </summary>
        public IPanel nextIPanel { get; set; }

        /// <summary>
        /// UIPanel显示层级设定
        /// </summary>
        public UILevel Level = UILevel.Common;

        /// <summary>
        /// UIPanel自身数据
        /// </summary>
        public IUIData UIData;
    }
        /// <summary>
    /// UIPanel层级分类
    /// </summary>
    public enum UILevel
    {
        None,
        //屏幕分层
        AlwayBottom = -3, //如果不想区分太复杂那最底层的UI请使用这个
        Bg = -2, //背景层UI
        AnimationUnderPage = -1, //动画层
        Common = 0, //普通层UI
        AnimationOnPage = 1, // 动画层
        PopUI = 2, //弹出层UI
        Guide = 3, //新手引导层
        Const = 4, //持续存在层UI
        Toast = 5, //对话框层UI
        Forward = 6, //最高UI层用来放置UI特效和模型
        AlwayTop = 7, //如果不想区分太复杂那最上层的UI请使用这个

        CanvasPanel = 100, // 最上层

        //眼镜端分层
        GlassesUIRoot = 199,//跟随屏幕移动C类UI
        FollowScreen = 200,//跟随屏幕移动C类UI
        FixedScreen = 201,//固定屏幕移动
    }
    /// <summary>
    /// UIPanel状态分类
    /// </summary>
    public enum PanelState
    {
        Opening = 0,//显示状态
        Hide = 1,//隐藏状态
        Closed = 2,//关闭状态
    }
    public enum UIType
    {
        Fragment,   // 非獨占,多個可共存
        Panel       // 獨占，只允許一個
    }
    /// <summary>
    /// 查找加载创建IPanel的数据类
    /// </summary>
    public class PanelSearchKeys
    {
        /// <summary>
        /// UIPanel的类型
        /// </summary>
        public Type PanelType;

        /// <summary>
        /// UIPanel预制加载路径
        /// </summary>
        public string Path;

        /// <summary>
        /// UIPanel名字
        /// </summary>
        public string Name;

        /// <summary>
        /// 是否UI层级显示在最上层
        /// </summary>
        public bool isUseOverlay;

        /// <summary>
        /// UIPanel显示层级设定
        /// </summary>
        public UILevel Level = UILevel.Common;

        /// <summary>
        /// UIPanel自身数据
        /// </summary>
        public IUIData UIData;
    }
```

当用代码生成一个 UI 界面后，需要根据用户的操作来显示或隐藏 UI 界面，所以我们需要把生成的 UI 界面统一管理起来，这个工作是通过 UIManager 来实现的
首先我们创建一个 UIPanel 的数据管理器
```csharp
/// <summary>
    /// UIPanel  数据管理器
    /// </summary>
    public class UIPanelTable : Singleton<UIPanelTable>
    {
        public UIPanelTable() { }

        /// <summary>
        /// 依据UIPanel类型的储存器,预制加载路径
        /// </summary>
        public Dictionary<string, IPanel> dic_AlIPanelsbyName = new Dictionary<string, IPanel>();

        /// <summary>
        /// 依据UIPanel类型的储存器
        /// </summary>
        public Dictionary<Type, IPanel> dic_AllPanelsbyType = new Dictionary<Type, IPanel>();
        /// <summary>
        /// UIPanel堆栈
        /// </summary>
        public Stack<IPanel> stack_panels = new Stack<IPanel>();

        public void OnAdd(IPanel panel)
        {
            if (dic_AllPanelsbyType.ContainsKey(panel.Info.PanelType))
            {
                dic_AllPanelsbyType[panel.Info.PanelType] = panel;
            }
            else
            {
                dic_AllPanelsbyType.Add(panel.Info.PanelType, panel);
            }
        }

        public void OnRemove(IPanel panel)
        {
            if (dic_AllPanelsbyType.ContainsKey(panel.Info.PanelType))
            {
                dic_AllPanelsbyType.Remove(panel.Info.PanelType);
            }
        }

        public void OnClear()
        {
            dic_AllPanelsbyType.Clear();
            stack_panels.Clear();
        }

        public IPanel GetPanelsByPanelSearchKeys(PanelSearchKeys panelSearchKeys)
        {
            if (dic_AllPanelsbyType.ContainsKey(panelSearchKeys.PanelType))
            {
                return dic_AllPanelsbyType[panelSearchKeys.PanelType];
            }
            return null;
        }


        public void OnPush(IPanel panel)
        {
            if (stack_panels.Contains(panel))
            {
                return;
            }
            stack_panels.Push(panel);
        }

        public IPanel OnPop()
        {
            if (stack_panels.Count <= 0)
            {
                return null;
            }
            return stack_panels.Pop();
        }

        public IPanel OnPeek()
        {
            if (stack_panels.Count <= 0)
            {
                return null;
            }
            return stack_panels.Peek();
        }

    }
```
同时我们添加了一个新接口 IUIManager
```csharp
public interface IUIManager
    {
        /// <summary>
        /// 打开UI
        /// </summary>
        /// <param name="panelSearchKeys"></param>
        /// <returns></returns>
        IPanel OpenUI(PanelSearchKeys panelSearchKeys);

        /// <summary>
        /// 显示UI
        /// </summary>
        /// <param name="panelSearchKeys"></param>
        void DisplayUI(PanelSearchKeys panelSearchKeys);

        /// <summary>
        /// 隐藏UI
        /// </summary>
        /// <param name="panelSearchKeys"></param>
        void HideUI(PanelSearchKeys panelSearchKeys);

        /// <summary>
        /// 关闭UI
        /// </summary>
        /// <param name="panelSearchKeys"></param>
        void CloseUI(PanelSearchKeys panelSearchKeys);

        /// <summary>
        /// 创建UI
        /// </summary>
        /// <param name="panelSearchKeys"></param>
        /// <returns></returns>
        IPanel CreateUI(PanelSearchKeys panelSearchKeys);

        /// <summary>
        /// 获取到UI
        /// </summary>
        /// <param name="panelSearchKeys"></param>
        /// <returns></returns>
        IPanel GetUI(PanelSearchKeys panelSearchKeys);

        /// <summary>
        /// 隐藏所有UI
        /// </summary>
        void HideAllUI();

        /// <summary>
        /// 关闭所有UI
        /// </summary>
        void CloseAllUI();

        /// <summary>
        /// 保存当前所有ui状态
        /// </summary>
        void StoreUIStates();

        /// <summary>
        /// 恢复之前所有ui状态
        /// </summary>
        void RestoreUIStates();
    }
public class UIManager : MonoBehaviour, IUIManager
    {
        /// <summary>
        /// UIPanel  数据管理器
        /// </summary>
        public UIPanelTable table { get { return UIPanelTable.Instance; } }
        /// <summary>
        /// UI 加载管理器
        /// </summary>
        public UILoaderFactory loaderFactory { get { return UILoaderFactory.Instance; } }
        public static UIManager Instance { get { return MonoSingletonProperty<UIManager>.Instance; } }

        #region 对外接口
        public IPanel OpenUI(PanelSearchKeys panelSearchKeys)
        {
            var currentPanel = table.GetPanelsByPanelSearchKeys(panelSearchKeys);

            if (currentPanel == null)
            {
                currentPanel = CreateUI(panelSearchKeys);
            }

            //记录UI队列
            if (currentPanel.Info.isRecord && currentPanel != table.OnPeek())
            {
                var prevPanel = table.OnPop();
                table.OnPush(currentPanel);

                if (prevPanel != null)
                {
                    // 打开panel后把上一个panel关闭
                    var uIType = GetPanelType(currentPanel.GetType());
                    if (uIType == UIType.Panel && GetPanelType(prevPanel.GetType()) == UIType.Panel)
                    {
                        prevPanel?.Hide();
                    }

                    prevPanel.Info.nextIPanel = currentPanel;
                    currentPanel.Info.prevIPanel = prevPanel;
                }
            }

            currentPanel.Open(panelSearchKeys.UIData);


            return currentPanel;
        }

        public UITypeAttribute GetAttributeByType(Type type)
        {
            var levelAtt = (UITypeAttribute)Attribute.GetCustomAttribute(type, typeof(UITypeAttribute));
            if (levelAtt == null)
            {
                Debug.LogWarning("UIPanel上缺少UITypeAttribute属性");
            }
            return levelAtt;
        }

        public UIType GetPanelType(Type type)
        {
            var att = GetAttributeByType(type);
            return att == null ? UIType.Fragment : att.uiType;
        }

        public IPanel GetTop()
        {
            return table.OnPeek();
        }

        public void DisplayUI(PanelSearchKeys panelSearchKeys)
        {
            var retPanel = table.GetPanelsByPanelSearchKeys(panelSearchKeys);

            if (retPanel != null)
            {
                retPanel.Display();
            }
        }

        public void ReturnToPreviousUI(PanelSearchKeys panelSearchKeys)
        {
            var currentPanel = table.GetPanelsByPanelSearchKeys(panelSearchKeys);

            if (currentPanel == null) return;
            if (currentPanel != table.OnPop()) return;
            var prevPanel = currentPanel.Info.prevIPanel;
            if (prevPanel == null) return;
            table.OnPush(prevPanel);

            if (prevPanel != null)
            {
                prevPanel.Info.prevIPanel = currentPanel;
                currentPanel.Info.nextIPanel = prevPanel;
            }
            currentPanel.Hide();
            prevPanel.Display();
        }

        public void HideUI(PanelSearchKeys panelSearchKeys)
        {
            var retPanel = table.GetPanelsByPanelSearchKeys(panelSearchKeys);

            if (retPanel != null)
            {
                retPanel.Hide();
            }
        }

        public void CloseUI(PanelSearchKeys panelSearchKeys)
        {
            var retPanel = table.GetPanelsByPanelSearchKeys(panelSearchKeys);

            if (retPanel != null)
            {
                retPanel.Close();
            }
        }

        public IPanel CreateUI(PanelSearchKeys panelSearchKeys)
        {
            IPanel panel = loaderFactory.LoadPanelPrefab(panelSearchKeys);

            if (panel != null)
            {
                panel.Init(panelSearchKeys);
                panel.SetConfig(loaderFactory.LoadPanelConfig(panelSearchKeys));

                table.OnAdd(panel);
                SetParentRootOfPanel(panel, loaderFactory.GetRootObject(panel));
                SetDefaultVauleOfPanel(panel);
            }
            return panel;
        }

        public IPanel GetUI(PanelSearchKeys panelSearchKeys)
        {
            return table.GetPanelsByPanelSearchKeys(panelSearchKeys);
        }

        public void HideAllUI()
        {
            foreach (var item in table.dic_AllPanelsbyType.Values)
            {
                item.Hide();
            }
        }

        public void CloseAllUI()
        {
            foreach (var item in table.dic_AllPanelsbyType.Values)
            {
                item.Close();
            }

            table.OnClear();
            // table.dic_AllPanelsbyType.Clear();
        }

        private Dictionary<IPanel, PanelState> dic_uiStates = new Dictionary<IPanel, PanelState>();
        public void StoreUIStates()
        {
            dic_uiStates.Clear();
            foreach (var item in table.dic_AllPanelsbyType.Values)
            {
                dic_uiStates.Add(item, item.State);
            }
        }

        public void RestoreUIStates()
        {
            foreach (KeyValuePair<IPanel, PanelState> pair in dic_uiStates)
            {
                if (pair.Value == PanelState.Opening)
                {
                    pair.Key.Display();
                }
                else if (pair.Value == PanelState.Hide)
                {
                    pair.Key.Hide();
                }
                else if (pair.Value == PanelState.Closed)
                {
                    pair.Key.Hide();
                }
            }
        }
        public void SetParentRootOfPanel(IPanel panel, Transform parentTransform)
        {
            panel.Transform.SetParent(parentTransform);
        }

        public void SetDefaultVauleOfPanel(IPanel panel)
        {
            RectTransform panelRectTrans = panel.Transform.GetComponent<RectTransform>();

            if (!panel.UseOriginRectTrans())
            {
                panelRectTrans.offsetMin = Vector2.zero;
                panelRectTrans.offsetMax = Vector2.zero;
                panelRectTrans.anchoredPosition3D = Vector3.zero;
                panelRectTrans.anchorMin = Vector2.zero;
                panelRectTrans.anchorMax = Vector2.one;
                panelRectTrans.localScale = Vector3.one;
                panelRectTrans.localRotation = Quaternion.identity;
                panelRectTrans.localPosition = Vector3.one;
            }
            else
            {
                panelRectTrans.anchoredPosition3D = Vector3.zero;
                panelRectTrans.localScale = Vector3.one;
                panelRectTrans.localRotation = Quaternion.identity;
                panelRectTrans.localPosition = Vector3.one;
            }
        }
        #endregion
    }
```
