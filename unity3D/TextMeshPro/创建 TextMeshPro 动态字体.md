首先，我们肯定要导入一份中文字体
![[Pasted image 20240403161823.png|500]]
然后我们在字体上右键，找到 Create-TextMeshPro-Font Asset
![[Pasted image 20240403161850.png|475]]
然后点击我们刚刚创建的字体文件，确保图示选项为 Dynamic(动态的)
![[Pasted image 20240403161949.png|388]]
然后我们把文件拖入到组件内，就可以输入中文字体了
![[Pasted image 20240403162248.png|500]]
在 Edit>Project Settings 中设置 TMP 的默认字体为刚刚生成的字体，就不用经常替换字体了
![[Pasted image 20240403163410.png|500]]
## 字体后备 Font Fallback
使用动态字体也有不方便，例如：使用思源宋体的.otf 生成的动态字体 Asset 在使用中文标点符号和一些特殊文字符号的时候，依旧会出现【方块】。并不能像静态字体一样用 txt 方便的加入需要的符号、文字。
这个时候可以使用TextMeshPro的Font Fallback。Font Fallback可以从另一个FontAsset中获取不包含在当前FontAsset中的字符。
我们可以用 Font Fallback 来外挂一些低频使用、或者特殊的符号、字体。
![[Pasted image 20240403170439.png|500]]

## 注意：
当中文字符过多时，会出现以下现象：
![[Pasted image 20240403162737.png|500]]
其实这个字体文件就是一个类似图集的东西，如果这个图集满了，动态生成就无法生成更多的字符了，所以只要我们让这个图集更大，就可以显示更多字符了：
![[Pasted image 20240403162825.png|450]] ![[Pasted image 20240403162835.png|525]]
或者，找到 TextMeshPro 的字体资源，在 GenerationSettings 中有一个 Multi [Atlas](https://so.csdn.net/so/search?q=Atlas&spm=1001.2101.3001.7020) Textures 选项，勾选上即可。
![[Pasted image 20240403163432.png|500]]
TextMeshPro 的动态字体是通过图集的方式实现的，而它默认生成的图集是一张 1024 x 1024 的图。
听起来很正常吧？可图集满了之后会干什么呢？
答案是放到一个 MissingCharacterList 里，然后用方框替代其显示出来
这是 TMP 默认创建动态字体会导致的行为，这实在是很 Unity！
那么这时候我们就要勾选 MultiAtlas 这个选项了，因为它会在检测到有没生成出的字体时，持续生成新的贴图。
