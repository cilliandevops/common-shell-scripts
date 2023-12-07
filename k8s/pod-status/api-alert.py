# author： cilliandevops
# time： 2023年12月7日15:51:33

# -*- coding: utf-8 -*-


import requests
from kubernetes import client, config
from kubernetes.client.rest import ApiException

# 企业微信机器人的webhook URL
webhook_url = ''

# 配置Kubernetes连接
config.load_kube_config(config_file="/etc/rancher/k3s/k3s.yaml")  # 假设你已经配置了kubectl本地访问K8s集群
v1 = client.CoreV1Api()

def send_alert_to_wechat(app_name, namespace, pod_name, phase):
    """
    向企业微信发送告警信息
    """

    message = {
        "msgtype": "text",
        "text": {
            "content": "警告：应用{0}在命名空间{1}中的Pod {2}状态异常，当前状态：{3}".format(app_name, namespace, pod_name, phase)
        }
    }

    headers = {'Content-Type': 'application/json'}
    response = requests.post(webhook_url, json=message, headers=headers)
    if response.status_code == 200:
        print("告警发送成功：{0} - {1}".format(app_name, pod_name))
    else:
        print("告警发送失败: {0}".format(response.text))

def check_pods_status():
    """
    检查所有Pods的状态，如果不是Running，则发送告警
    """
    try:
        pods = v1.list_pod_for_all_namespaces(watch=False)
        for pod in pods.items:
            if pod.status.phase != "Running":
                # 发送告警
                send_alert_to_wechat(pod.metadata.labels.get('app'), pod.metadata.namespace, pod.metadata.name, pod.status.phase)
    except ApiException as e:
        print("Exception when calling CoreV1Api->list_pod_for_all_namespaces: {0}".format(e))

# 设置脚本定期运行的时间间隔（例如60秒）
#import time
#while True:
check_pods_status()
#    time.sleep(60)

