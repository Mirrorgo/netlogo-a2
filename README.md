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

# DOING
- lwz: 优化现有代码,修改bug,详情参见lwz.ipynb

# TODO

> 尝试你的新模型。您能复制与原始 NetLogo 模型相同的行为吗?为什么/为什么不?你的实验应该研究模型参数对模型行为的影响。期望对两种模型的输出进行适当的统计分析，即原始NetLogo模型和您实现的模型;例如，报告和比较多个模型运行和参数值的模型的一些输出度量;这包括通过测量模型的输出来选择合理的方法来测量模型的行为

> 提出一个关于您所选择的 NetLogo 模型的问题，该问题需要对模型进行扩展才能回答(模型文档中的建议可能会提供一些想法，但我鼓励您生成自己的问题)。通过添加一个新颖的特征/行为来相应地扩展你的模型。设计并运行一个或多个实验，使您能够回答您制定的问题。最后，展示并讨论实验的结果

- [x] 实现代码逻辑
  - [ ] 优化代码，优化可读性 
- [ ] 验证模型(是否能复制相同的行为)
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




# 对extension的解释：
随着 **NEIGHBOR_INFLUENCE_PERCENTAGE（邻居影响百分比）** 增加，活跃叛乱的个体数逐渐减少，到达一个高值时叛乱几乎停止——可以从社会心理学和群体行为的角度进行解释。这种模式反映了个体行为对社群压力或社会规范的响应，以及这些因素如何影响集体行动。

### 社会同质性增加：
当 **NEIGHBOR_INFLUENCE_PERCENTAGE** 较高时，意味着个体的行为更多地受到周围人的影响。如果大多数人不处于激进状态，这种影响可能会使激进行为受到抑制。这相当于增加了社区中的同质性，个体更倾向于与周围人保持一致，减少了行为上的偏差。

### 社会稳定性和压力：
在高 **NEIGHBOR_INFLUENCE_PERCENTAGE** 的设置下，如果周围的大多数个体选择不叛乱，这种“不行动”的态度会通过社会影响力传递给其他成员，导致整体的叛乱活动降低。这种现象在现实世界中可以被看作是社会规范或压力对个体决策的显著影响，如社会和谐或公共秩序的压力导致公众不愿意进行抗议或叛乱。

### 减少的个体自主性：
较高的 **NEIGHBOR_INFLUENCE_PERCENTAGE** 可能意味着个体决策更多地受到集体意识的左右，减少了个体自主性和个体间行为的差异性。这在现实中可能对应于那些社会控制较严、个体自由受限的社会环境，其中个体行为更多地遵循集体规范或者上层指示。

### 缓和的激进行为：
在社会心理学中，人们在群体中可能会显示出与单独行动时不同的行为。当个体感知到大部分群体成员倾向于保持平静或遵守规则时，他们可能会抑制自己的激进行为以避免孤立。这种行为在社会动荡时期尤为明显，当公众普遍认为维持现状的成本低于变革成本时，更倾向于不采取行动。

这种模拟结果揭示了社会规范和集体影响力在控制和预防大规模社会动乱中的潜在作用。然而，这也表明过高的社会同质性可能抑制社会变革，可能导致问题和不满无法通过集体行动得到有效表达和处理。在设计社会政策或管理公共秩序时，理解和考虑这些动态非常关键。
