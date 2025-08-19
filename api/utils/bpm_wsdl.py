import configparser
from zeep import Client
import xml.etree.ElementTree as ET


class bpm_wsl(object):
    def __init__(self, ):
        # 載入WSDL
        config = configparser.ConfigParser()
        config.read('config.ini', encoding="utf-8")
        # self.wsdl = config.get('BPM', "wsdl_url")
        self.wsdl = 'http://192.168.70.115:8086/NaNaWeb/services/WorkflowService?wsdl'

    def __connect(self):
        try:
            self.client = Client(wsdl=self.wsdl)
            return self.client
        except Exception as e:
            self.client = False
            print('wsdl_init_error: ' + str(e))

    # 取得所有FUN資料
    def get_wsdl_fun_list(self):
        if self.__connect():
            try:
                # 獲取可用的操作
                operations = self.client.service._binding._operations
                # 列印每個操作的名稱
                for operation in operations.values():
                    print(f"Operation: {operation.name}")
            except Exception as e:
                return False, 'wsdl error:' + str(e)
            finally:
                # 關閉 zeep 客戶端
                self.client.transport.session.close()

    # 取得完整表單資料
    def get_all_xml_form(self, pSerialNo):
        if self.__connect():
            if not self.client:
                return False, f'wsdl error: Failed to connect to BPM service at {self.wsdl}'
            try:
                # 取得完整XML
                response = self.client.service.fetchFullProcInstanceWithSerialNo(pProcessInstanceSerialNo=pSerialNo)
                
                # 檢查響應是否為空
                if response is None:
                    return False, f'wsdl error: No response from BPM service for serial_no: {pSerialNo}'
                
                if not isinstance(response, str) or not response.strip():
                    return False, f'wsdl error: Empty or invalid response from BPM service for serial_no: {pSerialNo}. Response type: {type(response)}, Content: {response}'
                
                # 調試信息：記錄響應內容的前500個字符
                print(f"DEBUG: BPM response for {pSerialNo}: {response[:500]}...")
                
                # 處理回應
                try:
                    root = ET.fromstring(response)
                except ET.ParseError as parse_error:
                    return False, f'wsdl error: Invalid XML response from BPM service: {str(parse_error)}. Response: {response[:200]}...' 
                except Exception as xml_error:
                    return False, f'wsdl error: Failed to parse XML response: {str(xml_error)}. Response: {response[:200]}...' 
                # 取得表單資料
                act_forms_infos_dict = []
                act_forms_infos = root.findall('.//com.dsc.nana.services.webservice.FormInfo')
                for act_forms_info in act_forms_infos:
                    formId_el = act_forms_info.find('formId')
                    formId = formId_el.text if formId_el is not None and formId_el.text else 'N/A'
                    
                    serialNumber_el = act_forms_info.find('serialNumber')
                    serialNumber = serialNumber_el.text if serialNumber_el is not None and serialNumber_el.text else 'N/A'
                    
                    fieldValues_el = act_forms_info.find('fieldValues')
                    fieldValues = fieldValues_el.text if fieldValues_el is not None and fieldValues_el.text else 'N/A'
                    
                    act_forms_dict = {'formId': formId, 'serialNumber': serialNumber, 'fieldValues': fieldValues}
                    act_forms_infos_dict.append(act_forms_dict)
                    # print("---表單資料---")
                    # print(f"formId: {formId}")
                    # print(f"serialNumber: {serialNumber}")
                    # print(f"fieldValues: {fieldValues}")
                    # print("---表單資料---")
                # 取得流程基本資料 - 添加空值檢查
                processId_el = root.find('processId')
                processId = processId_el.text if processId_el is not None and processId_el.text else 'N/A'
                
                processName_el = root.find('processName')
                processName = processName_el.text if processName_el is not None and processName_el.text else 'N/A'
                
                createdTime_el = root.find('createdTime')
                createdTime = createdTime_el.text if createdTime_el is not None and createdTime_el.text else 'N/A'
                
                requesterId_el = root.find('requesterId')
                requesterId = requesterId_el.text if requesterId_el is not None and requesterId_el.text else 'N/A'
                
                requesterName_el = root.find('requesterName')
                requesterName = requesterName_el.text if requesterName_el is not None and requesterName_el.text else 'N/A'
                
                state_el = root.find('state')
                state = state_el.text if state_el is not None and state_el.text else 'N/A'
                
                OID_el = root.find('OID')
                OID = OID_el.text if OID_el is not None and OID_el.text else 'N/A'
                
                serialNo_el = root.find('serialNo')
                serialNo = serialNo_el.text if serialNo_el is not None and serialNo_el.text else 'N/A'
                
                subject_el = root.find('subject')
                subject = subject_el.text if subject_el is not None and subject_el.text else 'N/A'
                
                abortComment_el = root.find('abortComment')
                abortComment = abortComment_el.text if abortComment_el is not None and abortComment_el.text else 'N/A'
                # print("---流程目前狀態---")
                # print(f"流程代號: {processId}")
                # print(f"流程名稱: {processName}")
                # print(f"流程啟動時間: {createdTime}")
                # print(f"發起者的使用者代號: {requesterId}")
                # print(f"發起者的名字: {requesterName}")
                # print(f"流程目前狀態: {state}")
                # print(f"OID: {OID}")
                # print(f"serialNo: {serialNo}")
                # print(f"主旨: {subject}")
                # print(f"abortComment: {abortComment}")
                # print("---流程目前狀態---")

                # 提取活动信息
                act_instance_infos = root.findall('.//com.dsc.nana.services.webservice.ActInstanceInfo')
                activity_list = []
                for act_instance_info in act_instance_infos:
                    activity_id_el = act_instance_info.find('activityId')
                    activity_id = activity_id_el.text if activity_id_el is not None and activity_id_el.text else 'N/A'
                    
                    activity_name_el = act_instance_info.find('activityName')
                    activity_name = activity_name_el.text if activity_name_el is not None and activity_name_el.text else 'N/A'
                    
                    state_el = act_instance_info.find('state')
                    state = state_el.text if state_el is not None and state_el.text else 'N/A'
                    
                    started_time_el = act_instance_info.find('startedTime')
                    started_time = started_time_el.text if started_time_el is not None and started_time_el.text else 'N/A'
                    # print("---活動---")
                    # print(f"活動代號: {activity_id}")
                    # print(f"活動名稱: {activity_name}")
                    # print(f"活動目前狀態: {state}")
                    # print(f"活動第一次被啟動時間: {started_time}")  # 可以排訊啟動時間
                    # print("---活動---")
                    activity = {'activity_id': activity_id, 'activity_name': activity_name, 'state': state,
                                'started_time': started_time, 'signed_list': []}
                    signed_list = []
                    perform_infos = act_instance_info.findall('.//com.dsc.nana.services.webservice.PerformDetail')
                    for perform_info in perform_infos:
                        performerName_el = perform_info.find('performerName')
                        performerName = performerName_el.text if performerName_el is not None and performerName_el.text else 'N/A'
                        
                        notifiedName_el = perform_info.find('notifiedName')
                        notifiedName = notifiedName_el.text if notifiedName_el is not None and notifiedName_el.text else 'N/A'
                        
                        publicNotifiedName_el = perform_info.find('publicNotifiedName')
                        publicNotifiedName = publicNotifiedName_el.text if publicNotifiedName_el is not None and publicNotifiedName_el.text else 'N/A'
                        
                        privateNotifiedName_el = perform_info.find('privateNotifiedName')
                        privateNotifiedName = privateNotifiedName_el.text if privateNotifiedName_el is not None and privateNotifiedName_el.text else 'N/A'
                        
                        createdTime_el = perform_info.find('createdTime')
                        createdTime = createdTime_el.text if createdTime_el is not None and createdTime_el.text else 'N/A'
                        performedTime_element = perform_info.find('performedTime')
                        if performedTime_element is not None:
                            performedTime = performedTime_element.text
                        else:
                            performedTime = ''

                        comment_element = perform_info.find('comment')
                        if comment_element is not None:
                            comment = comment_element.text
                        else:
                            comment = ''

                        # //此tag內為每一次簽核內容, 有退回重辦或抽回重辦會有多個PerformInfo
                        # print("---簽合內容---")
                        # print(f"簽核者名字: {performerName}")
                        # print(f"通知名稱: {notifiedName}")
                        # print(f"公共通知名稱: {publicNotifiedName}")
                        # print(f"私人通知名稱: {privateNotifiedName}")
                        # print(f"工作建立的時間: {createdTime}")
                        # print(f"簽核者簽核時間: {performedTime}")
                        # print(f"簽核內容: {comment}")
                        # print("---簽合內容---")
                        signed = {'performerName': performerName, 'createdTime': createdTime,
                                  'performedTime': performedTime,
                                  'comment': comment}
                        signed_list.append(signed)
                    activity.update({'signed_list': signed_list})
                    activity_list.append(activity)
                # 匯總全部資料
                forms_info = {'processId': processId, 'processName': processName, 'createdTime': createdTime,
                              'requesterId': requesterId, 'requesterName': requesterName,
                              'state': state, 'OID': OID,
                              'serialNo': serialNo, 'subject': subject,
                              'abortComment': abortComment, 'form_list': act_forms_infos_dict,
                              'activity_list': activity_list
                              }
                # print(forms_info)
                # last_item = forms_info['activity_list'][-1]
                # print(last_item)
                # print(last_item['signed_list'][-1])
                return True, forms_info
            except Exception as e:
                return False, 'wsdl error:' + str(e)
            finally:
                if self.client and hasattr(self.client, 'transport'):
                    self.client.transport.session.close()
        else:
            return False, f'wsdl error: Failed to connect to BPM service at {self.wsdl}'

    # 取得簡單表單資料
    def fetchProcInstanceWithSerialNo(self, pSerialNo):
        if self.__connect():
            try:
                response = self.client.service.fetchProcInstanceWithSerialNo(pProcessInstanceSerialNo=pSerialNo)
                root = ET.fromstring(response)
                processId_el = root.find('processId')
                if processId_el is not None:
                    processId = processId_el.text
                    if processId is None:
                        processId = 'NA'
                else:
                    processId = 'NA'

                processName_el = root.find('processName')
                if processName_el is not None:
                    processName = processName_el.text
                    if processName is None:
                        processName = 'NA'
                else:
                    processName = 'NA'

                requesterId_el = root.find('requesterId')
                if requesterId_el is not None:
                    requesterId = requesterId_el.text
                    if requesterId is None:
                        requesterId = 'NA'
                else:
                    requesterId = 'NA'

                requesterName_el = root.find('requesterName')
                if requesterName_el is not None:
                    requesterName = requesterName_el.text
                    if requesterName is None:
                        requesterName = 'NA'
                else:
                    requesterName = 'NA'

                createdTime_el = root.find('createdTime')
                if createdTime_el is not None:
                    createdTime = createdTime_el.text
                    if createdTime is None:
                        createdTime = 'NA'
                else:
                    createdTime = 'NA'

                state_el = root.find('state')
                if state_el is not None:
                    state = state_el.text
                    if state is None:
                        state = 'NA'
                else:
                    state = 'NA'

                OID_el = root.find('OID')
                if OID_el is not None:
                    OID = OID_el.text
                    if OID is None:
                        OID = 'NA'
                else:
                    OID = 'NA'

                serialNo_el = root.find('serialNo')
                if serialNo_el is not None:
                    serialNo = serialNo_el.text
                    if serialNo is None:
                        serialNo = 'NA'
                else:
                    serialNo = 'NA'

                subject_el = root.find('subject')
                if subject_el is not None:
                    subject = subject_el.text
                    if subject is None:
                        subject = 'NA'
                else:
                    subject = 'NA'

                response_dict = {
                    'processId': processId, 'processName': processName, 'createdTime': createdTime,
                    'requesterId': requesterId, 'requesterName': requesterName, 'state': state, 'OID': OID,
                    'serialNo': serialNo, 'subject': subject
                }

                return True, response_dict
            except Exception as e:
                return False, 'wsdl error:' + str(e)
            finally:
                self.client.transport.session.close()

    # 同意審核
    def completeWorkItem(self, pWorkItemOID, pUserId, pComment='自動審核'):
        if self.__connect():
            try:
                response = self.client.service.completeWorkItem(pWorkItemOID=pWorkItemOID, pUserId=pUserId,
                                                                pComment=pComment)
                return True, response
            except Exception as e:
                print('wsdl_error:' + str(e))
                return False, 'wsdl error:' + str(e)
            finally:
                self.client.transport.session.close()

    # 更新work item 狀態為 開始('同意審核')
    def acceptWorkItem(self, pWorkItemOID, pUserId):
        if self.__connect():
            try:
                response = self.client.service.acceptWorkItem(pWorkItemOID=pWorkItemOID, pUserId=pUserId)
                return True, response
            except Exception as e:
                print('wsdl_error:' + str(e))
                return False, 'wsdl error:' + str(e)
            finally:
                self.client.transport.session.close()

    # 取回重辦
    def reexecuteActivity(self, pProcessSerialNo, pReexecuteActivityId, pAskReexecuteUserId,
                          pReexecuteComment='LINE_退回'):
        if self.__connect():
            try:
                response = self.client.service.reexecuteActivity(pProcessSerialNo=pProcessSerialNo,
                                                                 pReexecuteActivityId=pReexecuteActivityId,
                                                                 pAskReexecuteUserId=pAskReexecuteUserId,
                                                                 pReexecuteComment=pReexecuteComment)
                return True, response
            except Exception as e:
                print('wsdl_error:' + str(e))
                return False, 'wsdl error:' + str(e)
            finally:
                self.client.transport.session.close()

    # 已撤銷
    def abortProcessForSerialNo(self):
        if self.__connect():
            pass
        # response = client.service.abortProcessForSerialNo(pProcessInstanceSerialNo='APPFORMPROCESSPKG_ESSF0700000471',pAbortComment='已撤銷')

    # 已中止
    def terminatedProcessForSerialNo(self):
        if self.__connect():
            pass
        # response = client.service.terminatedProcessForSerialNo(pProcessInstanceSerialNo='APPFORMPROCESSPKG_ESSF0700000473',pUserId='1080401004',pTerminatedComment = '已中止')

    # 取得目前USER 待處理數量/通知
    def fetchWorkItemCount(self):
        if self.__connect():
            # 取得代辦數量  僅可傳入”0”或”1”。查詢「工作項目」輸入“0”；查詢「工作通知」輸入“1”。
            response = self.client.service.fetchWorkItemCount(pUserID='1100901001', pAccessCondition=0,
                                                              pViewTimesType='ALL')
            return response

    # 取得目前USER 待處理資料
    def fetchToDoWorkItem(self, userId, processIds=''):
        try:
            if self.__connect():
                response = self.client.service.fetchToDoWorkItem(pProcessIds=processIds, pUserId=userId)
                # 處理回應
                root = ET.fromstring(response)
                # 取得表單資料
                act_forms_infos_dict = []
                act_forms_infos = root.findall('.//com.dsc.nana.services.webservice.SimpleWorkItem')
                for act_forms_info in act_forms_infos:
                    processSerialNumber = act_forms_info.find('processSerialNumber').text
                    activityId = act_forms_info.find('activityId').text
                    workItemOID = act_forms_info.find('workItemOID').text
                    data = {'processSerialNumber': processSerialNumber, 'activityId': activityId,
                            'workItemOID': workItemOID}
                    act_forms_infos_dict.append(data)
                return True, act_forms_infos_dict
        except Exception as e:
            return False, 'wsdl error:' + str(e)
        finally:
            self.client.transport.session.close()

    # 取得工作狀態
    def checkWorkItemState(self, pWorkItemOID):
        try:
            if self.__connect():
                # 取得工作狀態 0 = 未有工作狀態 1＝以閱讀 3＝以同意 5＝被退回中 6＝以完成？
                response = self.client.service.checkWorkItemState(pWorkItemOID=pWorkItemOID)
                return True, int(response)
        except Exception as e:
            return False, 'wsdl error:' + str(e)
        finally:
            self.client.transport.session.close()

    # 查詢這個表單正在處理的工作項目
    def fetchProcInstances(self, pProcessId, pProcessInitialStartTime='', pProcessInitialEndTime='',
                           pProcInstanceState=''):
        try:
            if self.__connect():
                response = self.client.service.fetchProcInstances(pProcessId=pProcessId,
                                                                  pProcessInitialStartTime=pProcessInitialStartTime,
                                                                  pProcessInitialEndTime=pProcessInitialEndTime,
                                                                  pProcInstanceState=pProcInstanceState)
                print(response)

                return True, response
        except Exception as e:
            return False, 'wsdl error:' + str(e)
        finally:
            self.client.transport.session.close()


if __name__ == '__main__':
    wsdl = bpm_wsl()
    # dd = wsdl.fetchProcInstanceWithSerialNo('APPFORMPROCESSPKG_ESSF4700000001')
    # print(dd[1])
    # dd = wsdl.fetchProcInstances('APPFORMPROCESSPKG_ESSF47')
    # print(dd[1])
    # dd = wsdl.reexecuteActivity('APPFORMPROCESSPKG_ESSF0700000503', 'UserTask_3', '1080401004')
    # print(dd)
    # data = wsdl.get_all_xml_form('APPFORMPROCESSPKG_ESSF5100000499')
    data = wsdl.get_all_xml_form('PKG1753943982701100000063')
    # data1 = wsdl.fetchToDoWorkItem('1120301002', 'TEST0622')
    # data2 = wsdl.fetchToDoWorkItem('1121106002', 'TEST0622')
    # data3 = wsdl.acceptWorkItem('89e46c23f6c710048709f8ec01e2d3d5', '1100901001')
    # data2 = wsdl.checkWorkItemState('9d381231f6c910048709f8ec01e2d3d5')
    # print(data2)
    # if data2[1] == 0:
    #     data3 = wsdl.acceptWorkItem('9d381231f6c910048709f8ec01e2d3d5', '1120301002')
    #     print(f"{data3}:\n工作項目已接受")
    #     if data3[0]:
    #         data4 = wsdl.completeWorkItem('9d381231f6c910048709f8ec01e2d3d5', '1120301002', '自動審核')
    #         print(f"{data4}:\n工作項目已完成")
    # else:
    #     print(f"工作項目狀況為{data2[1]}:業務邏輯錯誤")
        
    print(data)
    # print(data1)
    # print(data2)
    # print(data4)
    # print(data5)
