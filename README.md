# 项目架构设计

针对"预约航班智能体"项目，在已有的 api / service / core 三层基础上，补充以下层级，并修正初版中存在的链路矛盾、职责重叠等问题。

## 目录结构

```text
flight_agent_project/

├── app/
│
│   ├── api/                         # API层：路由、参数校验、接收请求
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── chat.py          # 对话接口
│   │   │   │   ├── flight.py        # 航班查询/预约接口
│   │   │   │   └── user.py
│   │   │   └── router.py
│   │   └── deps.py                  # 依赖注入：注入 service / repository 实例，不直接暴露DB Session
│   │
│   ├── schemas/                     # Pydantic模型层（请求/响应数据结构）
│   │   ├── chat.py
│   │   ├── flight.py
│   │   ├── booking.py
│   │   └── user.py
│   │
│   ├── service/                     # Service层：业务逻辑实现（唯一的业务规则入口）
│   │   ├── chat_service.py          # 调用Agent进行对话
│   │   ├── flight_service.py        # 航班查询、余票校验等业务逻辑
│   │   ├── booking_service.py       # 预约规则、价格计算、订单状态机
│   │   └── user_service.py
│   │
│   ├── agent/                       # 智能体层（LangGraph相关，只做流程编排）
│   │   ├── graph.py                 # 构建LangGraph状态图
│   │   ├── state.py                 # 定义Agent State，字段尽量复用schemas中已有模型
│   │   │
│   │   ├── nodes/                   # 各个节点(Node)定义，节点本身不写业务规则
│   │   │   ├── intent_node.py       # 意图识别
│   │   │   ├── search_flight_node.py# 调用 flight_service 查询航班
│   │   │   ├── book_flight_node.py  # 调用 booking_service 完成预约
│   │   │   └── reply_node.py        # 生成回复
│   │   │
│   │   ├── tools/                   # Agent可调用工具(Tool)，仅做 service 调用 + LLM输入输出格式转换
│   │   │   ├── flight_tools.py      # 包装 flight_service，转换为LLM可用的tool schema
│   │   │   └── user_tools.py
│   │   │
│   │   └── prompts/                 # Prompt模板
│   │       ├── intent_prompt.py
│   │       └── reply_prompt.py
│   │
│   ├── memory/                      # LangGraph运行状态持久化（仅checkpoint，不含业务数据）
│   │   └── checkpoint.py            # checkpointer配置（连接redis/postgres/sqlite）
│   │
│   ├── models/                      # 数据库ORM模型
│   │   ├── flight.py
│   │   ├── booking.py
│   │   ├── session.py               # 用户与thread映射表（原session_manager的数据部分迁移至此）
│   │   └── user.py
│   │
│   ├── core/                        # 核心层：配置、数据库、异常等
│   │   ├── config.py                # 配置（读取.env、模型Key、DB地址等）
│   │   ├── database.py              # 数据库连接、Session管理（仅供repository使用）
│   │   ├── base_model.py            # ORM基类
│   │   ├── exceptions.py            # 自定义异常
│   │   └── security.py              # 鉴权/加密相关
│   │
│   ├── repository/                  # 数据访问层（DAO），唯一的数据库读写入口
│   │   ├── flight_repo.py
│   │   ├── booking_repo.py
│   │   ├── session_repo.py          # 会话ID与用户/thread映射的CRUD
│   │   └── user_repo.py
│   │
│   ├── utils/                       # 通用工具函数
│   │   ├── logger.py
│   │   └── helper.py
│   │
│   ├── middlewares/                 # 中间件
│   │   ├── logging_middleware.py    # 请求日志
│   │   └── exception_handler.py     # 全局异常处理，统一返回格式
│   │
│   └── main.py                      # 应用入口
│
├── tests/                           # 测试目录
│   ├── test_api/
│   ├── test_service/
│   ├── test_agent/
│   ├── test_repository/             # 新增：repository层单测
│   └── test_models/                 # 新增：models层单测
│
├── .env
├── requirements.txt
└── README.md
```

## 各层职责说明

- **schemas层**：定义API的请求/响应Pydantic模型，与数据库模型(models)解耦，便于参数校验和文档生成。

- **service层（业务规则唯一入口）**：所有业务规则（余票校验、预约规则、价格计算、用户额度等）必须收口在service层。无论请求来自api还是agent/tools，最终都通过service处理，避免业务规则绕过。

- **agent层（流程编排，瘦节点）**：单独成层，不塞入service。职责仅限于：
  - 维护LangGraph的图结构(node、edge、state)、prompt
  - 节点内部调用service完成具体业务，不自行实现业务规则
  - 便于单独测试agent的对话流程编排逻辑

- **agent/tools层**：作为service的"LLM适配层"，负责将service方法包装为LLM可调用的tool，并完成入参/出参与LLM所需的字符串/JSON格式之间的转换。tools**不直接调用repository**，统一经过service，保证业务规则一致。

- **models层**：纯数据库ORM模型，与schemas（接口数据结构）分离，遵循"内外数据结构隔离"原则。新增session表存储用户与thread的映射关系，归入models统一管理。

- **repository层（唯一数据库读写入口）**：把数据库CRUD操作从service中抽出，service只写业务逻辑，repository只写"怎么查/改数据库"。service通过依赖注入获取repository实例，不直接持有DB Session，避免绕层。

- **memory目录**：仅保留LangGraph checkpoint相关配置（如MemorySaver、Redis/Postgres checkpoint），用于多轮对话的运行状态持久化。原session_manager中的"用户↔thread映射"属于业务数据，已迁移至models/session.py + repository/session_repo.py。

## 调用链路（修正后）

统一为单一路径，避免agent与api各自访问数据层导致的业务规则不一致：

```text
api → service → repository → models/database (core)
                ↑
agent (LangGraph) → tools → service
```

- agent/tools 内部不再直接调用repository，统一通过调用service方法访问数据，service内部再调用repository完成CRUD。
- 这样无论入口是api还是agent，业务规则（如余票校验、预约状态机）都只在service层实现一次。

## State与Schema的关系

`agent/state.py` 中定义的State（TypedDict/Pydantic）应尽量复用 `schemas/` 中已定义的航班、订单等Pydantic模型作为字段类型，避免出现schemas、models、state三套重复的数据结构定义。state本身只新增对话流程相关的字段（如当前意图、对话历史引用、待确认的预约信息等）。

## 异常处理

`middlewares/exception_handler.py` 统一捕获 `core/exceptions.py` 中定义的自定义异常（如余票不足、预约冲突、鉴权失败等），转换为统一的响应格式返回给前端，便于调试智能体调用链。

## 补充建议

1. **依赖注入约束**：通过 `api/deps.py` 强制service层只能拿到repository实例，而不能直接持有DB Session，防止有人在service中绕过repository直接操作数据库。

2. **多轮记忆**：在 `memory/checkpoint.py` 中封装 LangGraph 的 checkpoint（如使用 `MemorySaver` 或 Redis/Postgres checkpoint）；用户与thread的业务映射关系走models/repository常规数据库路径。

3. **小型项目简化方案**：如果项目规模较小，可以省略repository层，将数据库操作直接写在service中；agent/tools仍统一调用service，保持"业务规则只在一处实现"这一原则不变。
