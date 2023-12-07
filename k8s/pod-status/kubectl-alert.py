# author： cilliandevops
# time： 2023年12月7日15:51:33

# -*- coding: utf-8 -*-

import subprocess
import requests
import json
import os

# 企业微信机器人的webhook URL
webhook_url = ''

# 定义被视为正常的Pod状态
normal_statuses = ['Running', 'Succeeded']

def send_alert_to_wechat(namespace, pod_name, status):
    """
    向企业微信发送告警信息
    """
    message = {
        "msgtype": "text",
        "text": {
            "content": "告警：命名空间'{namespace}'下的Pod '{pod_name}'状态为'{status}'，请立即关注。".format(
                namespace=namespace, pod_name=pod_name, status=status)
        }
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(webhook_url, json=message, headers=headers)
    if response.status_code == 200:
        print("告警已发送至企业微信：命名空间'{namespace}' 的 Pod '{pod_name}' 状态为 '{status}'。".format(
            namespace=namespace, pod_name=pod_name, status=status))
    else:
        print("告警发送失败：{text}".format(text=response.text))

def check_pods_status():
    """
    使用kubectl命令检查所有Pods的状态，如果不是在正常状态列表，则发送告警
    """
    cmd = "kubectl get pods --all-namespaces -o json"
    result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = result.communicate()
    
    if stderr:
        print("执行kubectl命令时出错: {error}".format(error=stderr.strip()))
        return

    pods = json.loads(stdout)

    for item in pods.get("items", []):
        namespace = item["metadata"]["namespace"]
        pod_name = item["metadata"]["name"]
        status = item["status"]["phase"]

        # 如果当前状态不在正常状态列表中，则发送告警
        if status not in normal_statuses:
            send_alert_to_wechat(namespace, pod_name, status)

if __name__ == "__main__":
    check_pods_status()

