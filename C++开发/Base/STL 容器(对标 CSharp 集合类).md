---
title: "[[STL 容器(对标 CSharp 集合类)]]"
type: Permanent
status: ing
Creation Date: 2026-06-20 14:58
tags:
---
STL = Standard Template Library,标准模板库,是 C++ 标准库的容器/算法部分,日常开发使用频率极高。

| C++ STL                   | C# 对应                       | 说明                            |
| ------------------------- | --------------------------- | ----------------------------- |
| `std::vector<T>`          | `List<T>`                   | 动态数组,最常用,连续内存                 |
| `std::array<T, N>`        | `T[]`(固定长度)                 | 固定大小数组                        |
| `std::list<T>`            | `LinkedList<T>`             | 双向链表                          |
| `std::deque<T>`           | —                           | 双端队列,头尾插入删除都快                 |
| `std::map<K,V>`           | `SortedDictionary<K,V>`     | 红黑树实现,按 key 有序,查找 O(log n)    |
| `std::unordered_map<K,V>` | `Dictionary<K,V>`           | 哈希表,无序,查找平均 O(1),**最常用的字典类型** |
| `std::set<T>`             | `SortedSet<T>`              | 有序去重集合                        |
| `std::unordered_set<T>`   | `HashSet<T>`                | 无序去重集合                        |
| `std::pair<A,B>`          | `(A,B)` 元组 / `KeyValuePair` | 二元组                           |
| `std::stack<T>`           | `Stack<T>`                  | 栈                             |
| `std::queue<T>`           | `Queue<T>`                  | 队列                            |
| `std::priority_queue<T>`  | `PriorityQueue<T>`(.NET 6+) | 优先队列(堆)                       |

## `std::vector` 常用操作
```cpp
#include <vector>
std::vector<int> v = {1, 2, 3};
v.push_back(4);            // 尾部添加,均摊 O(1)
v.pop_back();               // 移除最后一个
v.size();                   // 元素个数
v.empty();                  // 是否为空
v[0];                       // 索引访问,无边界检查
v.at(0);                    // 索引访问,有边界检查(越界抛 std::out_of_range)
v.clear();                  // 清空
v.insert(v.begin() + 1, 99); // 在指定位置插入(用迭代器定位)
v.erase(v.begin());          // 删除指定位置元素
  
for (auto& x : v) { /* ... */ }   // 遍历
```

## `std::unordered_map`(等价 C# `Dictionary`)
```cpp
#include <unordered_map>
std::unordered_map<std::string, int> scores;
scores["Tom"] = 90;            // 插入/修改,和 C# 字典语法一致
scores["Jerry"] = 85;

if (scores.find("Tom") != scores.end()) {   // 查找,find 返回迭代器,找不到返回 end()
    std::cout << scores["Tom"];
}

if (scores.count("Tom") > 0) {  // 另一种判断是否存在的写法
    // ...
}

for (auto& [name, score] : scores) {  // C++17 结构化绑定,遍历键值对(类似 C# foreach KeyValuePair)
    std::cout << name << ": " << score << std::endl;
}

scores.erase("Tom");             // 删除
```

⚠️ `map["key"]` 这种写法如果 key 不存在,会**自动插入一个默认值**(不像 C# 字典直接抛 `KeyNotFoundException`),只读查询时容易踩坑,推荐用 `find` 或 C++20 的 `contains()`。

## `std::pair`

```cpp
#include <utility>
std::pair<std::string, int> p = {"Tom", 90};
p.first;    // "Tom"
p.second;   // 90
auto [name, score] = p;   // C++17 结构化绑定拆包
```

## 迭代器与 `<algorithm>`

迭代器(iterator)是 STL 容器统一的遍历接口,行为类似指针,等价 C# 的 `IEnumerator`。
```cpp
std::vector<int> v = {1, 2, 3};
for (std::vector<int>::iterator it = v.begin(); it != v.end(); ++it) {
    std::cout << *it << std::endl;   // 解引用迭代器拿到元素
}
// 实际开发更推荐直接用 auto 或 range-for,很少手写完整迭代器循环
```
## `<algorithm>` 常用函数(等价 C# LINQ 的部分功能)

```cpp
#include <algorithm>
std::vector<int> v = {3, 1, 4, 1, 5};
std::sort(v.begin(), v.end());                          // 排序,等价 v.Sort() / OrderBy
std::sort(v.begin(), v.end(), [](int a, int b){ return a > b; }); // 自定义比较器(降序)

auto it = std::find(v.begin(), v.end(), 4);              // 查找,等价 IndexOf/Find
bool found = (it != v.end());

bool allPositive = std::all_of(v.begin(), v.end(), [](int x){ return x > 0; }); // 等价 All

int total = std::accumulate(v.begin(), v.end(), 0);       // 求和,等价 Sum(需要 #include <numeric>)

std::reverse(v.begin(), v.end());                          // 反转

int maxVal = *std::max_element(v.begin(), v.end());         // 最大值,等价 Max()

```
