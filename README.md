# DS Translator — Alfred Workflow

[English](README.en.md)

用 DeepSeek API 在 Alfred 里做**中英互译**，支持 `上下文 // 词语` 这种带场景的查词。

## 安装

1. 打开 **[Releases（最新版）](https://github.com/BitSparse/alfred_llm_translator/releases/latest)**，在 Assets 里下载 **DS-Translator.alfredworkflow**，双击导入 Alfred。（也可克隆本仓库后执行 `bash build.sh` 本地打包。）
2. 在 Alfred 里打开 **DS Translator**，点右上角 **[x]**，填写 [DeepSeek](https://platform.deepseek.com) 的 **API Key**。

## 用法

呼出 Alfred，输入：

```
tr hello
tr 法律 // brief
tr 编程 // variable
```


| 格式           | 含义          |
| ------------ | ----------- |
| `tr 词`       | 直接翻译，自动中英方向 |
| `tr 场景 // 词` | 按场景消歧，翻译更准  |


**回车** 复制当前条目到剪贴板。

## 其它

- 需要：**Alfred 5** + Powerpack、**Python 3**、DeepSeek 账号与 API Key。  
- 模型、温度等在 **Configure Workflow** 里可调，有默认值，一般不用动。

