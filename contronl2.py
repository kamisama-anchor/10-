from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
import threading
import time
import requests
from datetime import datetime


class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.flow_stats = {}  # 存储流表统计信息
        self.previous_flow_stats = {}  # 存储上一次的流表统计信息
        self.threshold = 10000  # 设置流量阈值 字节
        self.time_window = 5  # 设置时间窗口为 5 秒
        self.datapaths = {}  # 存储数据路径
        self.monitor_thread = threading.Thread(target=self._monitor)  # 创建监控线程
        self.monitor_thread.daemon = True  # 设置为守护线程
        self.monitor_thread.start()  # 启动监控线程
        self.packet_src = {}  # 在这里初始化 packet_src 字典

    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if not datapath.id in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    def _monitor(self):
        while True:
            for dp in self.datapaths.values():
                self.request_stats(dp)
            time.sleep(self.time_window)  # 每 5 秒获取一次统计信息

    def request_stats(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install table-miss flow entry
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None, idle_timeout=0, hard_timeout=0, rate_limit=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        if rate_limit:
            meter_id = self.create_meter(datapath, rate_limit)
            inst.append(parser.OFPInstructionMeter(meter_id))

        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst, idle_timeout=idle_timeout, hard_timeout=hard_timeout)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst, idle_timeout=idle_timeout, hard_timeout=hard_timeout)
        datapath.send_msg(mod)

    def create_meter(self, datapath, rate_limit):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        bands = [
            parser.OFPMeterBandDrop(rate=rate_limit, burst_size=0)
        ]
        mod = parser.OFPMeterMod(datapath, command=ofproto.OFPMC_ADD, flags=ofproto.OFPMF_KBPS, meter_id=1, bands=bands)
        datapath.send_msg(mod)
        return 1

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        body = ev.msg.body
        dpid = ev.msg.datapath.id
        current_time = time.time()

        if dpid not in self.flow_stats:
            self.flow_stats[dpid] = {}

        if dpid not in self.previous_flow_stats:
            self.previous_flow_stats[dpid] = {}

        # 获取源 MAC 地址（从packet_src中获取）
        src = self.packet_src.get(dpid, None)

        for stat in body:
            flow_key = (stat.cookie, stat.table_id, stat.priority, frozenset(stat.match.items()))
            if flow_key not in self.flow_stats[dpid]:
                self.flow_stats[dpid][flow_key] = {
                    'cookie': stat.cookie,
                    'duration': stat.duration_sec,
                    'table': stat.table_id,
                    'n_packets': stat.packet_count,
                    'n_bytes': stat.byte_count,
                    'priority': stat.priority,
                    'match': stat.match,
                    'actions': stat.instructions,
                    'last_update_time': current_time
                }
            else:
                previous_n_bytes = self.flow_stats[dpid][flow_key]['n_bytes']
                current_n_bytes = stat.byte_count
                byte_diff = current_n_bytes - previous_n_bytes
                last_update_time = self.flow_stats[dpid][flow_key]['last_update_time']
                time_diff = current_time - last_update_time

                if time_diff > 0 and byte_diff / time_diff > self.threshold / self.time_window:
                    output_port = None
                    for instruction in stat.instructions:
                        if isinstance(instruction, ev.msg.datapath.ofproto_parser.OFPInstructionActions):
                            for action in instruction.actions:
                                if isinstance(action, ev.msg.datapath.ofproto_parser.OFPActionOutput):
                                    output_port = action.port
                                    break
                            if output_port is not None:
                                break

                    if output_port is not None:
                        self.logger.info(f"Flow {flow_key} is abnormal: {byte_diff} bytes in {time_diff} seconds")
                        # 使用src进行决策
                        decision = self.vote_for_defense(byte_diff, time_diff, src)
                        if decision == 'block':
                            self.block_flow(ev.msg.datapath, stat.cookie, stat.match.get('in_port'), output_port)
                        elif decision == 'limit':
                            self.limit_flow_rate(ev.msg.datapath, stat.cookie, stat.match.get('in_port'), output_port, rate_limit=1000)  # 限制速率为 1000 字节/秒

                self.flow_stats[dpid][flow_key] = {
                    'cookie': stat.cookie,
                    'duration': stat.duration_sec,
                    'table': stat.table_id,
                    'n_packets': stat.packet_count,
                    'n_bytes': stat.byte_count,
                    'priority': stat.priority,
                    'match': stat.match,
                    'actions': stat.instructions,
                    'last_update_time': current_time
                }

        self.previous_flow_stats[dpid] = self.flow_stats[dpid].copy()


    def vote_for_defense(self, byte_diff, time_diff,src):
        # 投票裁决机制
        # 1. 如果流量速率大于阈值，认为有攻击
        # 2. 如果攻击强度很大，优先选择阻断
        # 3. 如果流量略有增加，则选择限速
        if byte_diff / time_diff > (self.threshold /self.time_window) * 1.5:  # 强烈攻击，阻断流量
         # 检测到攻击，发送警告到前端
            self.send_alert(src)
            return 'block'
        elif byte_diff / time_diff > self.threshold/self.time_window:  # 普通攻击，限速
            self.send_alert1(src)
            return 'limit'
        else:
            return 'no_action'  # 无需防御


    def block_flow(self, datapath, cookie, in_port, output):
        if int(datapath.id) in self.datapaths:
            for flow_key, flow in self.flow_stats[int(datapath.id)].items():
                if flow['cookie'] == cookie and flow['match'].get('in_port') == in_port:
                    for action in flow['actions'][0].actions:
                        if isinstance(action, datapath.ofproto_parser.OFPActionOutput) and action.port == output:
                            ofproto = datapath.ofproto
                            parser = datapath.ofproto_parser
                            match = flow['match']
                            actions = []  # 将动作设置为空
                            self.add_flow(datapath, 65535, match, actions)
                            self.logger.info(f"Blocked flow {flow_key}")
                            return
        self.logger.error(f"Flow with cookie {cookie}, in_port {in_port}, and output {output} not found in datapath {datapath.id}")
    def limit_flow_rate(self, datapath, cookie, in_port, output, rate_limit):
        if int(datapath.id) in self.datapaths:
            for flow_key, flow in self.flow_stats[int(datapath.id)].items():
                if flow['cookie'] == cookie and flow['match'].get('in_port') == in_port:
                    for instruction in flow['actions']:
                        if isinstance(instruction, datapath.ofproto_parser.OFPInstructionActions):
                            for action in instruction.actions:
                                if isinstance(action, datapath.ofproto_parser.OFPActionOutput) and action.port == output:
                                    ofproto = datapath.ofproto
                                    parser = datapath.ofproto_parser
                                    match = flow['match']
                                    actions = [parser.OFPActionOutput(output)]
                                    self.add_flow(datapath, 65535, match, actions, rate_limit=rate_limit)
                                    self.logger.info(f"Rate limited flow {flow_key} to {rate_limit} bytes/sec")
                                    return
        self.logger.error(f"Flow with cookie {cookie}, in_port {in_port}, and output {output} not found in datapath {datapath.id}")

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes", ev.msg.msg_len, ev.msg.total_len)
        
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return
        dst = eth.dst
        src = eth.src  # 获取源MAC地址

        dpid = format(datapath.id, "d").zfill(16)
        self.mac_to_port.setdefault(dpid, {})

        # 将src存储在self.packet_src字典中，dpid作为索引
        self.packet_src[dpid] = src

        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                return
            else:
                self.add_flow(datapath, 1, match, actions)
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

    def send_alert(self, src):
        alert_data = {
        "message": "发现攻击，攻击强度较大，进行流量阻断防御",
        "source": src,  # 保留攻击源信息
        "timestamp": datetime.now().isoformat()  # 添加时间戳
    }
        try:
            requests.post("http://127.0.0.1:8000/alert", json=alert_data)
        except Exception as e:
            self.logger.error("Failed to send alert: %s", str(e))
    def send_alert1(self, src):
        alert_data = {
        "message": "发现攻击，攻击强度较小，进行流量限制防御",
        "source": src,  # 保留攻击源信息
        "timestamp": datetime.now().isoformat()  # 添加时间戳
    }
        try:
            requests.post("http://127.0.0.1:8000/alert", json=alert_data)
        except Exception as e:
            self.logger.error("Failed to send alert: %s", str(e))
