# -*- coding: utf-8 -*-

import subprocess
import requests
import json

# 企业微信机器人的webhook URL
WEBHOOK_URL = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key='

def send_alert_to_wechat(namespace, pod_name, reason, message):
    """向企业微信发送告警信息"""
    content = "告警：命名空间'{}'下的Pod '{}'处于异常状态，原因：{}。{}".format(namespace, pod_name, reason, message)
    payload = {
        "msgtype": "text",
        "text": {"content": content}
    }
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(WEBHOOK_URL, data=json.dumps(payload), headers=headers)
    if response.status_code != 200:
        print("告警发送失败：HTTP状态码 {}".format(response.status_code))

def check_pods_status():
    """使用kubectl命令检查所有Pods的详细状态，如果存在异常，则发送告警"""
    cmd = "kubectl get pods --all-namespaces -o json"
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    
    if stderr:
        print("执行kubectl命令时出错: ", stderr.decode('utf-8').strip())
        return

    pods = json.loads(stdout)

    # 记录Pod状态的异常原因和消息
    for item in pods.get("items", []):
        namespace = item["metadata"]["namespace"]
        pod_name = item["metadata"]["name"]
        status = item["status"]["phase"]
        
        if status not in ["Running", "Succeeded"]:
            conditions = item["status"].get("conditions", [])
            container_statuses = item["status"].get("containerStatuses", [])
            
            for condition in conditions:
                if condition["status"] == "False":
                    send_alert_to_wechat(namespace, pod_name, condition["reason"], condition["message"])
                    break  # 发送一次告警即可，不需要重复告警

            for container_status in container_statuses:
                waiting = container_status.get("state", {}).get("waiting", {})
                if waiting and waiting.get("reason", "") not in ["ContainerCreating", "PodInitializing"]:
                    send_alert_to_wechat(namespace, pod_name, waiting["reason"], waiting.get("message", ""))
                    break  # 发送一次告警即可，不需要重复告警

if __name__ == "__main__":
    check_pods_status()

