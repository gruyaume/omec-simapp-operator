# simapp-operator

Open source 5G Core simapp Operator.

## Usage

```bash
juju deploy simapp-operator --trust --channel=edge
```
## Configuration

### **use-default-config**: Use default configuration (default: false)

This setting should only be used for testing purposes as it will use a default Network configuration with preset IMSI's and network slices.

If enabled, the following configuration file will be used:

```yaml
configuration:
  device-groups:
  - imsis:
    - "208930100007487"
    - "208930100007488"
    - "208930100007489"
    - "208930100007490"
    - "208930100007491"
    - "208930100007492"
    - "208930100007493"
    - "208930100007494"
    - "208930100007495"
    - "208930100007496"
    - "208930100007497"
    - "208930100007498"
    - "208930100007499"
    - "208930100007500"
    ip-domain-expanded:
      dnn: internet
      dns-primary: 8.8.8.8
      mtu: 1460
      ue-dnn-qos:
        bitrate-unit: bps
        dnn-mbr-downlink: 200000000
        dnn-mbr-uplink: 20000000
        traffic-class:
          arp: 6
          name: platinum
          pdb: 300
          pelr: 6
          qci: 9
      ue-ip-pool: 172.250.1.0/16
    ip-domain-name: pool1
    name: 5g-gnbsim-user-group1
    site-info: aiab
  - imsis:
    - "208930100007501"
    - "208930100007502"
    - "208930100007503"
    - "208930100007504"
    - "208930100007505"
    - "208930100007506"
    - "208930100007507"
    - "208930100007508"
    - "208930100007509"
    - "208930100007510"
    ip-domain-expanded:
      dnn: internet
      dns-primary: 8.8.8.8
      mtu: 1460
      ue-dnn-qos:
        bitrate-unit: bps
        dnn-mbr-downlink: 400000000
        dnn-mbr-uplink: 10000000
        traffic-class:
          arp: 6
          name: platinum
          pdb: 300
          pelr: 6
          qci: 8
      ue-ip-pool: 172.250.1.0/16
    ip-domain-name: pool2
    name: 5g-gnbsim-user-group2
    site-info: aiab2
  network-slices:
  - application-filtering-rules:
    - action: permit
      endpoint: 0.0.0.0/0
      priority: 250
      rule-name: ALLOW-ALL
    name: default
    site-device-group:
    - 5g-gnbsim-user-group1
    - 5g-gnbsim-user-group2
    site-info:
      gNodeBs:
      - name: aiab-gnb1
        tac: 1
      - name: aiab-gnb2
        tac: 2
      plmn:
        mcc: "208"
        mnc: "93"
      site-name: aiab
      upf:
        upf-name: upf
        upf-port: 8805
    slice-id:
      sd: "010203"
      sst: 1
  provision-network-slice: false
  sub-provision-endpt:
    addr: webui.my-network.svc.cluster.local
    port: 5000
  subscribers:
  - key: 5122250214c33e723a5dd523fc145fc0
    op: ""
    opc: 981d464c7c52eb6e5036234984ad0bcf
    plmnId: "20893"
    sequenceNumber: 16f3b3f70fc2
    ueId-end: "208930100007500"
    ueId-start: "208930100007487"
  - key: 5122250214c33e723a5dd523fc145fc0
    op: ""
    opc: 981d464c7c52eb6e5036234984ad0bcf
    plmnId: "20893"
    sequenceNumber: 16f3b3f70fc2
    ueId-end: "208930100007599"
    ueId-start: "208930100007501"
info:
  description: SIMAPP initial local configuration
  http-version: 1
  version: 1.0.0
logger:
  APP:
    ReportCaller: false
    debugLevel: info
```

## Image

- **simapp**: omecproject/simapp:main-a4f741a
