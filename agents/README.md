# 网络规划设计师备考 Agent 使用指南

> 目标：2026年11月14日通过考试

---

## 📚 Agent 概览

本项目提供3个专属Agent辅助备考：

| Agent | 类型 | 功能 | 使用场景 |
|-------|------|------|---------|
| **备考Agent** | Skill | 出题、批改、追踪薄弱点 | 日常练习、学习记录分析 |
| **刷题Agent** | Shell脚本 | 计时练习、考试模拟 | 模拟考试、限时训练 |
| **知识点讲解Agent** | Skill | 深入讲解、对比记忆 | 理解概念、攻克薄弱点 |

---

## 🚀 快速开始

### 1. 备考Agent - 日常练习

**启动方式：**
```bash
cd NetworkCertExam
claude
# 在Claude Code中输入 /skill exam-study
```

**常用命令：**

```bash
# 生成5道单选题练习
/quiz 5 single

# 生成3道案例分析题
/quiz 3 case

# 批改答案
/grade 245 B

# 查看薄弱点
/weak-points

# 查看学习进度
/progress
```

### 2. 刷题Agent - 模拟考试

**启动方式：**
```bash
cd NetworkCertExam
./scripts/exam-practice.sh 75 comprehensive  # 模拟真实考试（75题）
./scripts/exam-practice.sh 10 single         # 10道单选题练习
./scripts/exam-practice.sh 5 multi           # 5道多选题练习
```

**交互命令：**
- 输入答案（A/B/C/D）并回车
- 输入 `a` 显示答案
- 输入 `q` 退出练习

### 3. 知识点讲解Agent - 攻克难点

**启动方式：**
```bash
cd NetworkCertExam
claude
# 在Claude Code中输入 /skill knowledge-explainer
```

**常用命令：**

```bash
# 深入讲解知识点
/explain BGP路由黑洞
/explain SDN控制器
/explain 负载均衡算法

# 查看实际案例
/example 负载均衡
/example SDN

# 生成针对性练习
/practice BGP
/practice SDN

# 对比两个概念
/compare RAID5 vs RAID6
/compare SDN vs 传统网络
```

---

## 📋 学习流程建议

### 每日学习流程

1. **早上** - 使用备考Agent做5道选择题热身
   ```
   /quiz 5 single
   ```

2. **下午** - 使用刷题Agent进行限时训练
   ```bash
   ./scripts/exam-practice.sh 20 single
   ```

3. **晚上** - 使用知识点讲解Agent复习薄弱点
   ```
   /explain BGP路由黑洞
   /weak-points
   ```

### 薄弱点突破流程

1. 查看学习记录中的薄弱点
   ```
   /weak-points
   ```

2. 深入学习该知识点
   ```
   /explain [薄弱点名称]
   /example [薄弱点名称]
   ```

3. 做针对性练习
   ```
   /practice [薄弱点名称]
   ```

4. 记录到学习记录
   ```
   在每日一题/学习记录.md中更新
   ```

---

## 📁 相关文件

| 文件路径 | 说明 |
|---------|------|
| `data/exam.db` | 本地SQLite题库（757道题目） |
| `每日一题/学习记录.md` | 学习进度记录 |
| `每日一题/薄弱知识点专项学习_*.md` | 薄弱知识点资料 |
| `归纳总结资料/` | 归纳总结资料 |
| `scripts/query-questions.py` | 题目查询工具 |

---

## ⚙️ 数据访问

### 本地开发
```bash
# 直接查询题目
python scripts/query-questions.py --count 5 --type single

# 输出JSON格式
python scripts/query-questions.py --count 5 --json
```

### 生产环境 (Cloudflare D1)
```bash
# 查询生产数据
npx wrangler d1 execute networkcert-daily --remote --command "SELECT * FROM questions LIMIT 5;"

# 查看学习记录
npx wrangler d1 execute networkcert-daily --remote --command "SELECT * FROM question_history ORDER BY answered_at DESC LIMIT 10;"
```

---

## 🎯 考试信息

- **考试时间**：每年11月第二个星期六（2026年11月14日）
- **考试科目**：
  - 综合知识（75道选择题，75分）
  - 案例分析（3-5道问答题）
  - 论文（1道写作题）

---

## 📞 常见问题

**Q: Agent找不到题目？**
A: 检查 `data/exam.db` 是否存在，或使用 `python scripts/query-questions.py --count 5` 测试

**Q: 如何添加新题目？**
A: 通过Flask应用导入JSON格式题库，或直接编辑数据库

**Q: 学习记录如何同步？**
A: 学习记录保存在 `每日一题/学习记录.md`，定期提交到GitHub

---

*祝考试顺利！*
