# 运行指南（中文）

按顺序做，每一步都标了"你要做什么"和"检查什么"。预计总用时约一天。

## 0. 准备（10分钟）

```bash
cd stablecoin-evidence-talk
pip install -r requirements.txt
```

## 1. 收集语料（约1.5小时）

**你要做什么：**
1. 打开 `data/sources.csv`。已核实的链接已经填好；`url` 为空的行，按 `notes` 列的提示去官网找到原文链接，填进去
2. 储备报告（`doc_type` 为 `attestation` 的行）是PDF，从 Tether 和 Circle 的透明度页面下载
3. 运行：
   ```bash
   cd scripts
   python 01_collect.py
   ```
4. 有些网站会拦截脚本下载。脚本最后会列出失败的文件，请手动保存到 `data/raw/`，文件名必须是 `<doc_id>.html`、`.pdf` 或 `.txt`
   - 网页：浏览器"另存为"，或把正文复制到 `.txt` 文件里，段落之间空一行
   - X上的帖子：直接复制文字存成 `.txt`
5. 再跑一次 `python 01_collect.py`，它会记录每个文件的哈希值和获取时间

**检查：** `data/metadata.csv` 里每一行的 `status` 都是 `downloaded` 或 `present`。

**顺手做练习A：** 下载第一份储备报告后，打开 `analysis/report_comparison.md`，逐行填写。这就是速学包里的"五个问题"表格。

## 2. 清洗与拆段落（约30分钟，大部分时间在检查）

```bash
python 02_clean_segment.py
```

**检查：** 打开 `data/segments.csv`，每份文档抽看几段：
- 段落有没有被错误地切断或合并？
- 有没有残留的菜单、页脚、免责声明模板？
- 如果某份PDF提示"very little text"，说明是扫描件，可以先跳过

发现问题告诉我，我来调整清洗规则。

## 3. 人工先编30段，修订编码手册（约1小时）

这一步最重要，不要跳过。
1. 打开 `codebook/codebook_v0.1.yaml`，通读九个代码
2. 在 `segments.csv` 里挑30段（两家公司各半），自己贴标签
3. 记下：哪些段落难以归类？哪些定义模糊？是否需要新代码？
4. 修改编码手册，另存为 `codebook_v0.2.yaml`，把版本号改成 "0.2"
5. 在 `codebook/CHANGELOG.md` 里写清楚改了什么、为什么、是哪几段促成的

## 4. LLM编码（约30分钟）

```bash
export ANTHROPIC_API_KEY=你的key
python 03_llm_code.py --limit 20     # 先试20段，读一读结果合不合理
python 03_llm_code.py                # 再跑全部
```

用 DeepSeek 等兼容接口：
```bash
export LLM_PROVIDER=openai
export OPENAI_API_KEY=你的key
export OPENAI_BASE_URL=https://api.deepseek.com
export LLM_MODEL=deepseek-chat
python 03_llm_code.py
```

脚本会自动使用版本号最高的编码手册。中途断了可以直接重跑，已经编过的不会重复调用。

## 5. 人工盲编50段 + 一致性检验（约1小时）

```bash
python 04_sample_manual.py
```
1. 用 Excel 打开 `analysis/manual_coding.csv`
2. **不要看LLM的结果**，自己给每段在适用的代码列填 1
3. 有疑问写在 `notes` 列
4. 运行：
   ```bash
   python 05_agreement.py
   ```
5. 读 `analysis/disagreements.csv`：每一处分歧，判断是LLM错了、你错了，还是定义不清楚。定义不清就回到第3步修订编码手册

## 6. 描述性分析（约20分钟）

```bash
python 06_analysis.py
```
输出：
- `analysis/summary_tables.md`：各代码在两家公司、各事件时期的占比
- `analysis/figures/`：两张图
- `analysis/examples_by_code.md`：每个代码的代表性段落，下一步细读用

## 7. 细读（约1.5小时）

1. 读 `examples_by_code.md`，对照图表，写分析备忘录（直接写在 `memo.md` 草稿区，或另建笔记）
2. 重点读四个关键事件前后的文本：S&P降级、宣布四大审计、KPMG结果、OCC最终规则
3. 完成 `report_comparison.md`，比较报告实际提供的保证程度，与新闻稿里的说法
4. 检验设计文档中的四个假设：哪些成立？哪些被推翻？

## 8. 写备忘录与整理仓库（约1小时）

1. 按 `memo.md` 的大纲写两页备忘录
2. 更新 `README.md` 的 Findings 部分
3. 上传到 GitHub（`data/raw/` 已在 `.gitignore` 中排除，原始文件只保留链接）

## 遇到问题

- 下载失败：手动保存，见第1步
- 段落切分不对：把那份文档的 `doc_id` 和问题告诉我
- LLM返回格式错误：脚本会跳过并在下次运行时重试；如果反复失败，把错误信息发给我
