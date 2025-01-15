---
title: "[[弹窗类UI]]"
type: Permanent
status: done
Creation Date: 2024-02-18 15:09
tags:
---
下面是一个弹窗 UI 界面基类，提供最基础的弹框类功能
```csharp
public class PopupBase : MonoBehaviour
    {
        public virtual void Show()
        {
            this.gameObject.SetActive(true);
            this.OnShow();
        }

        public virtual void Hide()
        {
            this.OnHide();
            this.gameObject.SetActive(false);
        }

        public virtual void Close()
        {
            this.OnHide();
            this.OnClose();
        }

        protected virtual void OnShow() { }

        protected virtual void OnHide() { }

        protected virtual void OnClose()
        {
            if (gameObject != null)
            {
                GameObject.Destroy(gameObject);
            }
        }
    }
```
OnShow()、OnHide()、OnClose()这些方法在基类中定义，但不执行任何操作。这意味着子类可以选择性地重写这些方法，并在重写时提供自定义的逻辑。
使用 `protected` 访问修饰符的方法意味着这些方法只能在该类内部或其子类中访问，而不能在类外部直接访问。这种访问修饰符提供了一种封装的机制，允许类的实现细节在类的外部是不可见的，但在该类的派生类中是可见的。

接下来定义一个弹窗工厂的基类
```csharp
public class PopupFactoryBase<T> where T : PopupBase
{
    private static Transform _Root;
    public static Transform root
    {
        get
        {
            if (_Root == null)
            {
                if (Device.Instance.deviceType == DeviceType.Phone)
                {
                    var uiroot = Transform.FindObjectOfType<DefaultUIRoot>();
                    _Root = uiroot.PopUITrans;
                }
                else
                {
                    var glasses_root = Transform.FindObjectOfType<GlassesUIRoot>();
                    _Root = glasses_root.followScreenTrans;
                }
            }
            return _Root;
        }
    }
    public PopupFactoryBase() { }
        /// <summary>
        /// 需要保证T的类名与Prefab的名字一致
        /// </summary>
        /// <returns></returns>
    public virtual T Create()
    {
        var name = typeof(T).Name;
        T popup = GameObject.Instantiate<T>(Resources.Load<T>("UIModule/Popup/" + name), root);
        popup.transform.SetAsLastSibling();
        return popup;
    }
}
```
下面以一个一般性的弹窗为例，应用上述的基类
![[微信图片编辑_20240218153513.jpg|500]]

```csharp
public class CommonPopup : PopupBase
{
    public Button closeBtn;
    public Button cancelBtn;
    public Button confirmBtn;
    public Text titleName;
    public Text contentName;
    public Text cancelBtnName;
    public Text confirmBtnName;

    protected Action OnCloseClickAction;
    protected Action OnCancelClickAction;
    protected Action OnConfirmClickAction;

    public virtual void Start()
    {
        closeBtn?.onClick.AddListener(OnCloseClick);
        cancelBtn?.onClick.AddListener(OnCancelClick);
        confirmBtn?.onClick.AddListener(OnConfirmClick);
    }

    public CommonPopup SetConfirmAction(Action action)
    {
        this.OnConfirmClickAction = action;
        return this;
    }
	//点击确认按钮执行的动作，但是不会关闭弹窗
    public CommonPopup SetConfirmActionWithOutClose(Action action)
    {
        this.OnConfirmClickAction = action;
        return this;
    }

    public CommonPopup SetTitle(string title)
    {
        if (!string.IsNullOrEmpty(title))
        {
            this.titleName.text = title;
        }
        return this;
    }

    public CommonPopup SetContent(string content)
    {
        if (!string.IsNullOrEmpty(content))
        {
            this.contentName.gameObject.SetActive(true);
            this.contentName.text = content;
        }
        else
        {
            this.contentName.gameObject.SetActive(false);
        }
        return this;
    }

    public CommonPopup SetConfirmBtnInteractable(bool flag)
    {
        if (this.confirmBtn)
        {
            this.confirmBtn.interactable = flag;
        }
        return this;
    }

    public CommonPopup SetCancelBtnInteractable(bool flag)
    {
        if (this.cancelBtn)
        {
            this.cancelBtn.interactable = flag;
        }
        return this;
    }

    public CommonPopup SetCancelBtnActive(bool flag)
    {
        if (this.cancelBtn)
        {
            this.cancelBtn.gameObject.SetActive(flag);
        }
        return this;
    }

    public CommonPopup SetCloseAction(Action action)
    {
        this.OnCloseClickAction = action;
        return this;
    }

    public CommonPopup SetCancelAction(Action action)
    {
        this.OnCancelClickAction = action;
        return this;
    }

    public CommonPopup SetInfo(string title, string content, string confirmText, string cancelText, Action onConfirm, Action onCancel, Action onClose)
    {
        if (!string.IsNullOrEmpty(title))
        {
            this.titleName.text = title;
        }
        if (!string.IsNullOrEmpty(content))
        {
            this.contentName.text = content;
        }
        if (!string.IsNullOrEmpty(confirmText))
        {
            this.confirmBtnName.text = confirmText;
        }
        if (!string.IsNullOrEmpty(cancelText))
        {
            this.cancelBtnName.text = cancelText;
        }
        this.OnCloseClickAction = onClose;
        this.OnConfirmClickAction = onConfirm;
        this.OnCancelClickAction = onCancel;
        return this;
    }
    public virtual void OnCloseClick()
    {
        OnCloseClickAction?.Invoke();
        this.Close();
    }
    public virtual void OnCancelClick()
    {
        OnCancelClickAction?.Invoke();
        this.Close();
    }
    public virtual void OnConfirmClick()
    {
        OnConfirmClickAction?.Invoke();
        this.Close();
    }
}
public class CommonPopupFactory : CommonPopupFactory<CommonPopup> { }
```
有了这个一般性弹窗的类之后呢，我们再创建一个一般性弹窗的工厂类，通过这个工厂类，可以方便地创建 CommonPopup 类型的弹出窗口，并且可以根据需求设置弹出窗口的各种属性信息，从而实现了对弹出窗口的定制化。
```csharp
public class CommonPopupFactory<T> : PopupFactoryBase<T> where T : CommonPopup
{
    private string mTitle = "";
    private string mContent = "";
    private string mConfirmBtnTitle = "";
    private string mCancelBtnTitle = "";
    private bool mConfirmBtnInteractable = true;
    private bool mCancelBtnInteractable = true;
    private bool mCancelBtnActive = true;
    private Action onConfirm;
    private Action onCancel;
    private Action onClose;

    public CommonPopupFactory<T> SetTitle(string title)
    {
        this.mTitle = title;
        return this;
    }

    public CommonPopupFactory<T> SetContent(string content)
    {
        this.mContent = content;
        return this;
    }

    public CommonPopupFactory<T> SetConfirmBtnTitle(string title)
    {
        this.mConfirmBtnTitle = title;
        return this;
    }

    public CommonPopupFactory<T> SetCancelBtnTitle(string title)
    {
        this.mCancelBtnTitle = title;
        return this;
    }

    public CommonPopupFactory<T> SetConfirmBtnInteractable(bool interactable)
    {
        this.mConfirmBtnInteractable = interactable;
        return this;
    }

    public CommonPopupFactory<T> SetCancelBtnInteractable(bool interactable)
    {
        this.mCancelBtnInteractable = interactable;
        return this;
    }

    public CommonPopupFactory<T> SetCancelBtnActive(bool interactable)
    {
        this.mCancelBtnActive = interactable;
        return this;
    }

    public CommonPopupFactory<T> SetConfirmAction(Action action)
    {
        this.onConfirm = action;
        return this;
    }

    public CommonPopupFactory<T> SetConfirmActionWithOutClose(Action action)
    {
        this.onConfirm = action;
        return this;
    }

    public CommonPopupFactory<T> SetCancelAction(Action action)
    {
        this.onCancel = action;
        return this;
    }

    public CommonPopupFactory<T> SetCloseAction(Action action)
    {
        this.onClose = action;
        return this;
    }

    public override T Create()
    {
        T popup = base.Create();
        popup.SetInfo(mTitle, mContent, mConfirmBtnTitle, mCancelBtnTitle, onConfirm, onCancel, onClose);
        popup.SetConfirmBtnInteractable(mConfirmBtnInteractable);
        popup.SetCancelBtnInteractable(mCancelBtnInteractable);
        popup.SetCancelBtnActive(mCancelBtnActive);
        return popup;
    }
}
```