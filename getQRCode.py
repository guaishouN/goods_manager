import requests
import configparser
import json
import qrcode
from PIL import Image, ImageDraw, ImageFont
import time

def get_tenant_access_token(app_id=None, app_secret=None, config_file=None):
    # 构建请求URL和请求头
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
    }

    # 构建请求体
    payload = {
        "app_id": app_id,
        "app_secret": app_secret
    }

    # 发起请求
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response_json = response.json()
    return response_json.get('code'), response_json.get('tenant_access_token')


def list_records(tenant_access_token=None, app_token=None, table_id=None, page_token=None, page_size=None, config_file=None):
    if config_file is None:
        config_file = 'feishu-config.ini'

    config = configparser.ConfigParser()
    config.read(config_file, encoding='utf-8')
    if not page_token:
        page_token = config.get('LIST_RECORDS', 'page_token', fallback=None)
    if not page_size:
        page_size = config.get('LIST_RECORDS', 'page_size', fallback=100)

    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
    headers = {
        'Authorization': 'Bearer ' + tenant_access_token,
        'Content-Type': 'application/json; charset=utf-8',
    }
    params = {'page_size': page_size}
    if page_token:
        params['page_token'] = page_token

    response = requests.get(url, headers=headers, params=params)
    records = response.json()
    items = records.get('data', {}).get('items', [])
    return records.get('code'), items


def get_simple_qr_data(item):
    """
    item is json object like this:
    item={'fields': {'人员': [{'avatar_url': 'https://s3-imfile.feishucdn.com/static-resource/v1/v2_f034f39f-0cd0-40e6-8e97-e0db60a3e8bg~?image_size=72x72&cut_type=default-face&quality=&format=jpeg&sticker_format=.webp', 'email': 'guihui.deng@desaysv.com', 'en_name': 'Deng Guihui', 'id': 'ou_8936da90a34fef1e63f1187fd758d889', 'name': '邓桂辉'}], '使用状态': '否', '多选': ['深圳', '在用'], '日期': 1704384000000, '讨论群': [{'avatar_url': 'https://s3-imfile.feishucdn.com/static-resource/avatar/v2_d248c8e8-95c3-4a1a-acde-132a922ca14g_96.webp', 'id': 'oc_6487afe936188a67dc010a716af6b050', 'name': 'ARD2 SW4'}], '设备编号': '22222223666666', '附件': None, '项目': '23MM Hi Plus'}, 'id': 'recokkcOCR', 'record_id': 'recokkcOCR'}
    qr_data is json object like this:
    qr_data = {'Uid': 'recokkcOCR', 'User': '邓桂辉', 'date': '2024/01/05', 'No.': '22222223666666', 'Proj': '23MM Hi Plus'}
    """
    # item to qr_data
    try:
        qr_data = {}
        fields = item.get('fields', {})
        qr_data['Uid'] = item.get('record_id', '')
        qr_data['User'] = fields.get('人员', [{}])[0].get('name', '')
        #date format: 2024/01/05
        time_stamp = fields.get('日期', 0)
        qr_data['date'] = time.strftime("%Y/%m/%d", time.localtime(time_stamp/1000))
        qr_data['No.'] = fields.get('设备编号', '')
        qr_data['Proj'] = fields.get('项目', '')
    except Exception as e:
        print(f'####got exception:{e}')
        qr_data = None
    return qr_data


def simplify_records(items)->list:
    """
    records is json object like this:
    records = {'code': 0, 'data': {'has_more': False, 'items': [{'fields': {'人员': [{'avatar_url': 'https://s3-imfile.feishucdn.com/static-resource/v1/v2_f034f39f-0cd0-40e6-8e97-e0db60a3e8bg~?image_size=72x72&cut_type=default-face&quality=&format=jpeg&sticker_format=.webp', 'email': 'guihui.deng@desaysv.com', 'en_name': 'Deng Guihui', 'id': 'ou_8936da90a34fef1e63f1187fd758d889', 'name': '邓桂辉'}], '使用状态': '否', '多选': ['深圳', '在用'], '日期': 1704384000000, '讨论群': [{'avatar_url': 'https://s3-imfile.feishucdn.com/static-resource/avatar/v2_d248c8e8-95c3-4a1a-acde-132a922ca14g_96.webp', 'id': 'oc_6487afe936188a67dc010a716af6b050', 'name': 'ARD2 SW4'}], '设备编号': '22222223666666', '附件': None, '项目': '23MM Hi Plus'}, 'id': 'recokkcOCR', 'record_id': 'recokkcOCR'}, {'fields': {'人员': [{'avatar_url': 'https://s3-imfile.feishucdn.com/static-resource/v1/v2_f034f39f-0cd0-40e6-8e97-e0db60a3e8bg~?image_size=72x72&cut_type=default-face&quality=&format=jpeg&sticker_format=编号': '22222dfghj', '附件': None, '项目': '23MM Hi Plus'}, 'id': 'rec5CaQsTa', 'record_id': 'rec5CaQsTa'}, {'fields': {'人员': [{'avatar_url': 'https://s3-imfile.feishucdn.com/static-resource/v1/v2_f034f39f-0cd0-40e6-8e97-e0db60a3e8bg~?image_size=72x72&cut_type=default-face&quality=&format=jpeg&sticker_format=.webp', 'email': 'guihui.deng@desaysv.com', 'en_name': 'Deng Guihui', 'id': 'ou_8936da90a34fef1e63f1187fd758d889', 'name': '邓桂辉'}], '使用状态': '是', '多选': None, '日期': 1704902400000, '讨论群': [{'avatar_url': 'https://s3-imfile.feishucdn.com/static-resource/v1/default-avatar_100f43a5-7dfc-4cba-8eac-93ca9496a96d~?image_size=72x72&cut_type=&quality=&format=jpeg&sticker_format=.webp', 'id': 'oc_e66d0de25ad374f7794215c9b3235ec6', 'name': '安享管家证书更换方案检讨'}], '设备编号': '1123588', '附件': None, '项目': 'g\u2006j\u2006j\u2006j'}, 'id': 'recUgaeMwu', 'record_id': 'recUgaeMwu'}, {'fields': {'人员': None, '使用状态': None, '多选': None, '日期': None, '讨论群': None, '设备编号': None, '附件': None, '项目': None}, 'id': 'recy9dpWvY', 'record_id': 'recy9dpWvY'}], 'page_token': 'recy9dpWvY', 'total': 4}, 'msg': 'success'} 
    """    
    for item in items:
        qr_data=get_simple_qr_data(item)
        if qr_data is None:
            continue
        yield qr_data

def gen_qrcode_by_qr_data(qr_data):
    """
    qr_data is json object like this:
    {'Uid': 'rec5CaQsTa', 'User': '邓桂辉', 'date': 1704384000000, 'No.': '22222dfghj', 'Proj': '23MM Hi Plus'}
     use pillow to generate qrcode
    """
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    info = f"Uid: {qr_data['Uid']}\nUser: {qr_data['User']}\nDate: {qr_data['date']}\nNo.: {qr_data['No.']}\nProj: {qr_data['Proj']}"
    qr.add_data(info)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    text_lines = info.split('\n')
    # Create a new image with white background
    new_image = Image.new("RGB", (400+450, 450), "white")

    # Get a drawing context
    draw = ImageDraw.Draw(new_image)

    # Set a font
    #font = ImageFont.load_default()
    font_size=34
    font = ImageFont.truetype("msyhl.ttc", font_size)

    # Set the position to start drawing the text
    text_position = (20, 50)

    # Write each line of text
    for line in text_lines:
        draw.text(text_position, line, font=font, fill="black")
        text_position = (text_position[0], text_position[1] + font_size+18)

    # Paste the original image on the right side
    new_image.paste(img, (400, 0))

    # Save the result
    new_image.save(f"./qrcodes/qrcode_{qr_data['Uid']}.png")
  

app_id = 'cli_a514aea9fa79900b'
app_secret = 'IsUeIxmzO5NtJiQA6B3MdfkHqIcmQqws'
app_token = 'CmHmb4MxPaEW7zsWB07c1hCUnhd'
table_id = 'tbl3OBzMMqjX79gN'
record_id = 'recokkcOCR'
fields = """{
  "fields": {
    "使用状态": "否"
  }
}"""
code1, tenant_access_token = get_tenant_access_token(app_id=app_id, app_secret=app_secret)
print(f'code1:{code1} tenant_access_token:{tenant_access_token}')
code2, items = list_records(tenant_access_token=tenant_access_token, app_token=app_token, table_id=table_id)
print(f'code2:{code2} records sizes:{len(items)}')
for qr_data in simplify_records(items):
    print(f'qr_data:{qr_data}\n')
    gen_qrcode_by_qr_data(qr_data)
    


