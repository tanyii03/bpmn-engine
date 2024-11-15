import abc
from .gateway import Gateway
from datetime import datetime

import logging

logger = logging.getLogger(__name__)

class ParallelGateway(Gateway):
    
    def execute(self,context,payload):
        self._execute(context,payload)
        name = self.name
        task = self.task_context
        
        context[name]["start_time"] = datetime.now()        
        context[name]["end_time"] = datetime.now()

        self.payload_task = payload[name]
        payload_task = self.payload_task

        # if self.process_instance.handler != None:
        #     if hasattr(self.process_instance.handler,f"on_enter_{name}"):
        #         getattr(self.process_instance.handler,f"on_enter_{name}")(context = context,task = payload_task, payload = payload, process_instance = self.process_instance)
        self.process_instance.evaluate_results(self.get_outgoing_activities())

    def outgoing_flow_success(self,flow_id):
        context = self.context
        if context.get(flow_id) == None:
            context[flow_id] = {}

        context[flow_id]["start_time"] = datetime.now()        
        context[flow_id]["end_time"] = datetime.now()
        context[flow_id]["id"] = flow_id

    def is_all_incoming_complete(self):
        incomingflowids = self.activity_data[1].get("incoming")
        source_activity_refs=[]
        if type(incomingflowids) == type([]):
            for incomingflowid in incomingflowids:
                for seq_flow in self.process_instance.diagram.get_flows():
                    if(seq_flow[2].get("id") == incomingflowid):
                        source_activity_refs.append(seq_flow[2].get("sourceRef"))

        source_activity_names = []
        for source_activity_ref in source_activity_refs:
            for node in self.process_instance.diagram.get_nodes():
                    if node[1].get("id") == source_activity_ref:
                        source_activity_names.append(node[1].get("node_name"))

        for source_activity_name in source_activity_names:
            if(self.context.get(source_activity_name,{}).get("status","NOT_DEFINED") != "COMPLETED"):
                return False

        return True

    def get_outgoing_activities(self):

        if self.is_all_incoming_complete() != True:
            return None
        context = self.context
        payload = self.payload
        outgoingflowids = self.activity_data[1].get("outgoing")
        
        if type(outgoingflowids) != type([]):
            outgoingflowids = [outgoingflowids]

        target_activity_ids=[]
        if type(outgoingflowids) == type([]):
            for outgoingflowid in outgoingflowids:
                for seq_flow in self.process_instance.diagram.get_flows():
                    if(seq_flow[2].get("id") == outgoingflowid):
                        target_activity_ids.append(seq_flow[2].get("targetRef"))
                        self.outgoing_flow_success(outgoingflowid)

        targets = []

        logger.info(target_activity_ids)

        for target_activity_id in target_activity_ids:
            for node in self.process_instance.diagram.get_nodes(): 
                if node[1].get("id") == target_activity_id:
                    target_activity_data = node
                    target_activity_type = node[1].get("type")
                    targets.append((target_activity_type,target_activity_id,target_activity_data))          
        return targets