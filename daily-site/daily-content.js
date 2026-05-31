// daily-content.js - 每日学习内容生成器
// 运行方式: node daily-content.js [日期YYYY-MM-DD]

const StudyContent = {
  // 阶段一：案例分析突破（6月）
  phase1: {
    title: "案例分析突破",
    theme: "案例分析专项训练",
    days: [
      {
        day: 1,
        date: "2026-06-01",
        topic: "第一题：网络系统规划设计与优化",
        tags: ["SDN", "无线网络", "负载均衡"],
        knowledge: [
          {
            title: "SDN控制器作用",
            points: [
              "网络可编程，配置自动化",
              "流量调度灵活，优化带宽利用",
              "故障快速响应，自动化恢复",
              "统一管控，简化运维"
            ]
          },
          {
            title: "无线网络部署关键因素",
            points: [
              "覆盖范围和信号强度",
              "接入容量和并发用户数",
              "信道规划和干扰规避",
              "终端兼容性",
              "安全策略（Portal/802.1X）"
            ]
          },
          {
            title: "出口负载均衡策略",
            points: [
              "基于目的地址的策略路由",
              "教育网地址段走教育网出口",
              "其他流量默认走运营商出口"
            ]
          }
        ],
        caseFramework: [
          "【问题1】优化措施：SDN控制器集中管控、无线AP补盲、多出口负载均衡、VLAN标准化、自动化运维",
          "【问题2】SDN部署位置：核心层或独立集中部署；改进作用：可编程、流量调度、故障恢复、统一管控",
          "【问题3】无线部署因素：覆盖范围、接入容量、信道规划、干扰规避、终端兼容、安全策略",
          "【问题4】出口负载均衡：策略路由基于目的地址，教育网走教育网出口，其他走运营商出口"
        ]
      },
      {
        day: 2,
        date: "2026-06-02",
        topic: "第二题：网络安全防护方案设计",
        tags: ["防火墙", "IDS", "VPN", "ACL", "态势感知"],
        knowledge: [
          {
            title: "防火墙部署与作用",
            points: [
              "防火墙1：互联网与DMZ之间，边界防护，控制外部对DMZ访问",
              "防火墙2：DMZ与内网之间，分区隔离，保护内网",
              "防火墙是主动防御（主动阻止）"
            ]
          },
          {
            title: "IDS入侵检测系统",
            points: [
              "旁路部署，不影响网络性能",
              "特征库匹配检测已知攻击",
              "行为分析检测异常流量",
              "优点：可双向检测；缺点：无法主动阻断"
            ]
          },
          {
            title: "VPN技术对比",
            points: [
              "SSL VPN：移动办公、Web应用远程接入，仅需浏览器",
              "IPSec VPN：Site-to-Site固定场所互联，需专业客户端",
              "记忆口诀：移动办公用SSL，站点互联用IPSec"
            ]
          }
        ],
        caseFramework: [
          "【问题1】防火墙1：互联网-DMZ边界防护；防火墙2：DMZ-内网分区隔离；IDS：旁路入侵检测；VPN：远程接入加密",
          "【问题2】态势感知平台核心功能：全网安全事件采集、威胁检测预警、资产可视化、应急响应联动、态势预测",
          "【问题3】ACL工作原理：按规则顺序匹配，匹配即执行，未匹配隐含deny。示例：permit tcp 10.1.0.0 0.0.255.255 10.2.0.0 0.0.255.255 eq 80",
          "【问题4】VPN应用场景：远程移动办公、总部分支机构互联、第三方人员接入。SSL VPN适合移动办公，IPSec VPN适合Site-to-Site"
        ]
      },
      {
        day: 3,
        date: "2026-06-03",
        topic: "第三题：传输网络规划与设计",
        tags: ["SDH", "MSTP", "OTN", "DWDM", "环形保护"],
        knowledge: [
          {
            title: "传输技术对比",
            points: [
              "SDH：同步数字体系，成熟可靠，用于语音业务",
              "MSTP：多业务传送平台，在SDH上集成以太网",
              "OTN：光传送网，大容量、智能光交换，支持多种业务",
              "DWDM：密集波分复用，极高容量用于骨干网"
            ]
          },
          {
            title: "OTN主要优势",
            points: [
              "大带宽：单波长可达100G甚至更高",
              "业务适配性：支持SDH/以太网/视频多种业务",
              "智能光交换：波长路由、动态分配",
              "高可靠性：光环保护"
            ]
          },
          {
            title: "环形保护方式",
            points: [
              "通道保护环：业务双发双收，倒换时间<50ms",
              "复用段保护环：利用K1/K2字节倒换，倒换时间<50ms",
              "区别：通道保护面向业务，复用段保护面向链路"
            ]
          }
        ],
        caseFramework: [
          "【问题1】技术对比：SDH成熟可靠用于语音，MSTP集成以太网，OTN大容量智能，DWDM极高容量骨干。OTN优势：大带宽、多业务适配、智能光交换",
          "【问题2】通道保护环：业务双发双收，倒换快；复用段保护环：利用K1/K2倒换，链路级别。适用场景：通道保护适合话音业务，复用段保护适合数据业务",
          "【问题3】可靠性设计：设备冗余（双主控、双电源）、链路冗余（双上联）、网络拓扑（环形组网）、自动倒换",
          "【问题4】推荐方案：从技术成熟度和兼容性角度，MSTP或OTN均可支持多业务。推荐OTN，因其支持SDH/以太网/视频且扩展性好"
        ]
      }
    ]
  },

  // 综合知识高频考点
  comprehensiveKnowledge: {
    week1: {
      title: "计算机基础",
      topics: [
        {
          name: "CSMA/CD",
          points: ["载波监听多路访问/冲突检测", "先听后发，边发边听，冲突停发，随机重发"]
        },
        {
          name: "PPP协议",
          points: ["LCP建立配置数据链路", "NCP分配网络层地址", "支持PAP/CHAP认证"]
        },
        {
          name: "HDLC",
          points: ["面向比特的同步协议", "信息帧、监督帧、无编号帧", "位填充实现透明传输"]
        }
      ]
    },
    week2: {
      title: "网络协议",
      topics: [
        {
          name: "TCP三次握手",
          points: ["SYN_SENT → SYN_RCVD → ESTABLISHED", "seq序列号，ack确认号"]
        },
        {
          name: "ARP协议",
          points: ["将IP地址解析为MAC地址", "广播请求，单播响应", "ARP缓存表"]
        },
        {
          name: "DNS记录类型",
          points: ["A记录：域名→IPv4", "AAAA：域名→IPv6", "MX：邮件服务器", "CNAME：别名"]
        }
      ]
    },
    week3: {
      title: "设备与配置",
      topics: [
        {
          name: "VLAN划分",
          points: ["基于端口（最常用）", "基于MAC地址", "基于协议", "基于IP子网"]
        },
        {
          name: "生成树协议STP",
          points: ["防止网络环路", "选举根桥", "阻塞非根端口", "快速收敛用RSTP/MSTP"]
        },
        {
          name: "OSPF路由协议",
          points: ["Router ID标识路由器", "邻接关系建立", "LSA泛洪", "区域划分"]
        }
      ]
    }
  },

  // 论文高频方向
  essayDirections: [
    {
      title: "SDN在企业网络中的应用",
      outline: "项目背景 → SDN架构设计 → 控制器部署 → 流量调度优化 → 运维自动化 → 效果评价",
      template: "20XX年X月，我作为项目经理主持了XX单位网络系统升级项目。针对网络配置复杂度高、运维效率低等问题，设计了基于SDN的集中管控方案。部署SDN控制器后，实现了流量自动调度、故障快速响应，网络运维效率提升40%，获得了用户高度认可。"
    },
    {
      title: "网络安全防护体系建设",
      outline: "安全风险分析 → 防护架构设计 → 防火墙部署 → IDS联动 → 态势感知 → 日志审计",
      template: "20XX年X月，我参与XX单位网络安全防护体系建设项目。针对其面临的外部攻击和内部威胁，设计了分层防护方案。部署防火墙、IDS、VPN网关等设备，建立态势感知平台，形成整体防护体系。项目运行后，安全事件下降60%。"
    },
    {
      title: "无线网络规划与部署",
      outline: "需求分析 → 覆盖设计 → AP部署 → 信道规划 → 安全策略 → 效果验证",
      template: "20XX年X月，我负责XX园区无线网络覆盖项目。针对无线信号盲区、接入容量不足等问题，制定了高密放装方案。通过合理AP布局、信道规划，实现了无死角覆盖，支持XX并发用户接入，用户满意度显著提升。"
    }
  ]
};

// 生成指定日期的学习内容
function getDailyContent(date) {
  const baseDate = new Date('2026-06-01');
  const targetDate = new Date(date);
  const dayDiff = Math.floor((targetDate - baseDate) / (1000 * 60 * 60 * 24));

  // 案例分析阶段（6月每天一道）
  if (dayDiff >= 0 && dayDiff < 30) {
    const phaseIndex = Math.floor(dayDiff / 10);
    const dayInPhase = dayDiff % 10;
    const topic = [
      "第一题：网络系统规划设计与优化",
      "第二题：网络安全防护方案设计",
      "第三题：传输网络规划与设计",
      "第四题：网络存储与计算平台设计",
      "第五题：网络故障诊断与排除"
    ][phaseIndex];

    return {
      type: "case",
      topic: topic,
      knowledge: StudyContent.phase1.days[phaseIndex % 3].knowledge,
      framework: StudyContent.phase1.days[phaseIndex % 3].caseFramework,
      tags: StudyContent.phase1.days[phaseIndex % 3].tags
    };
  }

  // 综合知识阶段
  if (dayDiff >= 30 && dayDiff < 60) {
    return {
      type: "comprehensive",
      topic: "综合知识 - " + StudyContent.comprehensiveKnowledge.week1.title,
      knowledge: StudyContent.comprehensiveKnowledge.week1.topics,
      tags: ["选择题", "高频考点"]
    };
  }

  // 默认返回综合知识
  return {
    type: "comprehensive",
    topic: "综合知识 - 计算机网络基础",
    knowledge: StudyContent.comprehensiveKnowledge.week1.topics,
    tags: ["选择题"]
  };
}

// 输出JSON供前端使用
const date = process.argv[2] || new Date().toISOString().split('T')[0];
console.log(JSON.stringify(getDailyContent(date), null, 2));