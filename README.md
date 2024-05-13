# 环境准备
- 必须插件
  - Jupyter
  - Netlogo Syntax Highlighting
- 推荐插件
  - Markdown All in One 

# 项目结构
- origin.nlogo放置源文件
- comment.nlogo可以随便改注释
- share.ipynb自由讨论+一些代码的分享
  - 其他的交流再微信群里面
- scripts里面放最终报告所需的所有代码

# DOING
- 

# TODO

> 尝试你的新模型。您能复制与原始 NetLogo 模型相同的行为吗?为什么/为什么不?你的实验应该研究模型参数对模型行为的影响。期望对两种模型的输出进行适当的统计分析，即原始NetLogo模型和您实现的模型;例如，报告和比较多个模型运行和参数值的模型的一些输出度量;这包括通过测量模型的输出来选择合理的方法来测量模型的行为

> 提出一个关于您所选择的 NetLogo 模型的问题，该问题需要对模型进行扩展才能回答(模型文档中的建议可能会提供一些想法，但我鼓励您生成自己的问题)。通过添加一个新颖的特征/行为来相应地扩展你的模型。设计并运行一个或多个实验，使您能够回答您制定的问题。最后，展示并讨论实验的结果

- [x] 实现代码逻辑
  - [x] 优化代码，优化可读性 
- [x] 验证模型(是否能复制相同的行为)
  - [ ] 
- [ ] 设计问题
- [ ] 扩展
  - [ ] 生成异步更新的版本
  - [ ] 找其他的...
- [ ] 生成csv版本的结果&&去掉plot (最后再做)
- [ ] 研究netlogo的csv导出
- [ ] 每次的访问可能是随机的,so用下shaffle

# Version
- v1 (by lc)
  - 完成功能逻辑
- model_v4_lc_new.py 最新的模型，这一版老师说ok了
- model_v4_lc_extension.py
  - 添加了extension，新增了neighbor的不满程度对个体不满程度的影响。可以修改neighbor影响的百分比。
- v4.5 (by lwz)5
- 
  - 修改了一些逻辑，用另一种方式实现的功能，但奇怪的是目前和lc的运行结果相同，但是和netlogo不同。
  - 此外，目前这个版本运行较慢，还是需要增加数组存储neighbor增加运行速度
- 4.1 和4.7(by lwz)
  - 更改统计方式, 与netlogo更加类似了,但是仍有差距
  - 增加了起始的点
- 4.2 & 4.8
  - 尝试去掉自己计算一些值，但是好像没啥区别
  - 尝试去掉自己，但是好像没啥区别


