#_*_coding:utf-8_*_
GET_TASK_URL='GET_TASK_URL'




GET_VISITOR_INFO='GET_VISITOR_INFO'

STATUS_FINISH='STATUS_FINISH'



# msg type, could be REGISTER, UNREGISTER and HEARTBEAT
MSG_TYPE	= 'TYPE'

# send register
REGISTER 	= 'REGISTER'

# unregister client with id assigned by master
UNREGISTER 	= 'UNREGISTER'

# send heart beat to server with id
HEARTBEAT	= 'HEARTBEAT'

# notify master paused with id
PAUSED 		= 'PAUSED'

# notify master resumed with id
RESUMED		= 'RESUMED'

# notify master resumed with id
SHUTDOWN		= 'SHUTDOWN'

# client id key word
CLIENT_ID 	= 'CLIENT_ID'

# server status key word
ACTION_REQUIRED	= 'ACTION_REQUIRED'

# server require pause
PAUSE_REQUIRED	= 'PAUSE_REQUIRED'

# server require pause
RESUME_REQUIRED	= 'RESUME_REQUIRED'

# server require shutdown
SHUTDOWN_REQUIRED	= 'SHUTDOWN_REQUIRED'

# server status key word
SERVER_STATUS	= 'SERVER_STATUS'

# server status values
STATUS_RUNNING	= 'STATUS_RUNNING'

STATUS_PAUSED 	= 'STATUS_PAUSED'

STATUS_SHUTDOWN	= 'STATUS_SHUTDOWN'

STATUS_CONNECTION_LOST	= 'STATUS_CONNECTION_LOST'

ERROR 	= 'ERROR'

# client id not found, then it needs to register itself
ERR_NOT_FOUND	= 'ERR_NOT_FOUND'


#自定义,主要用于master和server之间的交互,主要用于更新带爬取的数据队列.
ADD_TASK_URL='ADD_TASK_URL'

MSG_RECV_OK="MSG_RECV_OK"

SEND_BACK_DATA="SEND_BACK_DATA"

CLIENT_STOP="CLIENT_STOP"


NEED_TO_SEND_MASTER="NEED_SEND_TO_MASTER"



#master中，需要处理的几种数据类型，如添加任务队列，数据存储等：
DATA_TYPE_SAVERESULT='DATA_TYPE_SAVERESULT'
DATA_TYPE_ADDTASKURL='DATA_TYPE_ADDTASKURL'