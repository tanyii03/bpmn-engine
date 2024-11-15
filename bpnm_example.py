#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bpmn import bpmn_diagram_rep as diagram
from engine.bpmn_process import BpmnProcess
import logging

logging.basicConfig(level=logging.INFO)

bpmn_diagram = diagram.BpmnDiagramGraph()
bpmn_diagram.load_diagram_from_xml_file("default-conditional-flow-example.bpmn")



tasks = bpmn_diagram.get_nodes()
for task in tasks:
    print(task)

flows = bpmn_diagram.get_flows()
for flow in flows:
    print(flow)


logging.info("Starting process")
engine = BpmnProcess()
engine.start_process(bpmn_diagram)
