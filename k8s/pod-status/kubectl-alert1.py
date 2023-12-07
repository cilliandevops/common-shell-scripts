# author： cilliandevops
# time： 2023年12月7日15:51:33

# -*- coding: utf-8 -*-

import subprocess
import requests
import json
import os

# 企业微信机器人的webhook URL
webhook_url = ''

def send_alert_to_wechat(namespace, pod_name, reason, message):
    """
    向企业微信发送告警信息
    """
    content = "告警：命名空间'{}'下的Pod '{}'处于异常状态，原因：{}。{}".format(namespace, pod_name, reason, message)
    payload = {
        "msgtype": "text",
        "text": {
            "content": content
        }
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(webhook_url, json=payload, headers=headers)
    if response.status_code == 200:
        print("告警已发送至企业微信：", content)
    else:
        print("告警发送失败：", response.text)

def check_pods_status():
    """
    使用kubectl命令检查所有Pods的详细状态，如果存在异常，则发送告警
    """
    cmd = "kubectl get pods --all-namespaces -o json"
    result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = result.communicate()
    
    if stderr:
        print("执行kubectl命令时出错: ", stderr.strip())
        return

    pods = json.loads(stdout)

    # 记录Pod状态的异常原因和消息
    for item in pods.get("items", []):
        namespace = item["metadata"]["namespace"]
        pod_name = item["metadata"]["name"]
        status = item["status"]["phase"]
        if status != "Running" and status != "Succeeded":  # 如果Pod不处于运行或成功完成状态
            # 检查status.conditions和status.containerStatuses以获取详细的异常信息
            conditions = item["status"].get("conditions", [])
            container_statuses = item["status"].get("containerStatuses", [])
            for condition in conditions:
                if condition["status"] == "False":
                    reason = condition["reason"]
                    message = condition["message"]
                    send_alert_to_wechat(namespace, pod_name, reason, message)
                    break  # 发送一次告警即可，不需要重复告警
            for container_status in container_statuses:
                waiting = container_status.get("state", {}).get("waiting", {})
                if waiting and waiting.get("reason", "") not in ["ContainerCreating", "PodInitializing"]:
                    reason = waiting["reason"]
                    message = waiting.get("message", "")
                    send_alert_to_wechat(namespace, pod_name, reason, message)
                    break  # 发送一次告警即可，不需要重复告警

if __name__ == "__main__":
    check_pods_status()

