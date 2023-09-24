LINQ（Language Integrated Query）是一种用于在.NET 平台上进行数据查询和操作的技术。它是由微软推出的一种语言集成查询的技术，可以通过统一的语法风格对各种数据源进行查询和操作，包括对象集合、数据库、XML 文档等。

使用 LINQ，开发人员可以使用统一的查询语法来进行各种数据操作，而无需关心底层数据源的差异。LINQ 提供了一组标准的查询操作符，例如 `Where`、`Select`、`OrderBy` 等，可以用于对数据进行筛选、投影、排序等操作。此外，LINQ 还提供了强大的表达式树功能，可以在运行时动态构建和执行查询表达式。
## 1. Where
LINQ 中的 `Where` 方法是用于筛选数据源中符合指定条件的元素。它是 LINQ 查询语句中最常用的筛选操作符之一。
`Where` 方法接受一个 lambda 表达式作为参数，该表达式定义了筛选条件。对于数据源中的每个元素，`Where` 方法会根据 lambda 表达式的逻辑判断该元素是否满足条件。如果满足条件，则该元素会被保留下来，否则将被过滤掉。
`Where` 方法的语法如下：
```csharp
IEnumerable<TSource> Where<TSource>(this IEnumerable<TSource> source, Func<TSource, bool> predicate)
```
其中，`source` 是要进行筛选的数据源，可以是任何实现了 `IEnumerable<TSource>` 接口的类型。`predicate` 是一个 lambda 表达式，它接受一个参数表示数据源中的每个元素，并返回一个布尔值，表示该元素是否满足筛选条件。

例如，假设有一个整型数组 `numbers`，我们想筛选出其中大于 5 的元素，可以使用 `Where` 方法进行筛选：
```csharp
int[] numbers = { 2, 5, 8, 10, 3 };
IEnumerable<int> filteredNumbers = numbers.Where(n => n > 5);
```
在上述代码中，lambda 表达式 `n => n > 5` 表示判断元素是否大于 5 的条件。`Where` 方法会遍历 `numbers` 数组中的每个元素，对每个元素应用 lambda 表达式的逻辑，如果返回值为 `true`，则该元素会被保留下来，最后返回一个包含符合条件的元素的 `IEnumerable<int>` 序列。
## 2.Aggregate
LINQ 中的 `Aggregate` 方法用于对数据源进行累积操作，将所有元素按照指定的逻辑进行聚合。

`Aggregate` 方法接受两个参数：初始值和一个累积函数。初始值是累积的起始值，累积函数定义了对每个元素进行累积操作的规则。

`Aggregate` 方法的语法如下：
```csharp
TAccumulate Aggregate<TSource, TAccumulate>(this IEnumerable<TSource> source, TAccumulate seed, Func<TAccumulate, TSource, TAccumulate> func)
```
其中，`source` 是要进行累积操作的数据源，可以是任何实现了 `IEnumerable<TSource>` 接口的类型。`seed` 是初始值，表示累积的起始值。`func` 是一个累积函数，它接受两个参数：`accumulate` 表示当前的累积结果，`next` 表示数据源中的下一个元素。累积函数的返回值将作为下次累积的结果。

下面是一个示例，使用 `Aggregate` 方法计算整型数组中所有元素的和：
```csharp
int[] numbers = { 4, 7, 10 };
int sum = numbers.Aggregate(0, (accumulate, next) => accumulate + next);
```
在上述代码中，初始值为 0，累积函数 `(accumulate, next) => accumulate + next` 表示将当前的累积结果 `accumulate` 加上下一个元素 `next`，得到新的累积结果。

`Aggregate` 方法会遍历数据源中的每个元素，将初始值和第一个元素作为参数传递给累积函数，计算得到一个中间结果。然后，将这个中间结果与下一个元素作为参数传递给累积函数，继续计算得到新的中间结果。直到遍历完所有元素，最终得到累积的结果。

在上述示例中，计算的过程为：0 + 4 = 4，4 + 7 = 11，11 + 10 = 21，所以 `sum` 的值为 21。