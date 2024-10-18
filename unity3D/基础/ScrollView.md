滚动列表的居中显示效果
```csharp
internal void ScrolleToIndex(int index, int totalCount)
{
    var contentRoot_width = _keyPointListRoot.GetComponent<RectTransform>().sizeDelta.y;
    var width = contentRoot_width / totalCount;
    var scrolleView_width = _keyPointScrollView.GetComponent<RectTransform>().sizeDelta.y;

    if (contentRoot_width < scrolleView_width)
    {
        return;
    }
    var step = width / (contentRoot_width - scrolleView_width);
    var step_count = index - (int)(scrolleView_width / width) / 2;
    if (step_count < 0)
    {
        return;
    }

    var scrolle_value =1- Mathf.Clamp(step_count * step, 0, 1);
    _keyPointListRoot.parent.parent.GetComponent<ScrollRect>().verticalNormalizedPosition = scrolle_value;
}
```