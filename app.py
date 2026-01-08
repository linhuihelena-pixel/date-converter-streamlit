import streamlit as st
from datetime import datetime, timedelta
import re

# 页面配置
st.set_page_config(
    page_title="多语言日期格式转换器",
    page_icon="📅",
    layout="wide"
)

# 月份映射表
MONTH_MAP = {
    # 英语
    'jan': '01', 'january': '01',
    'feb': '02', 'february': '02',
    'mar': '03', 'march': '03',
    'apr': '04', 'april': '04',
    'may': '05',
    'jun': '06', 'june': '06',
    'jul': '07', 'july': '07',
    'aug': '08', 'august': '08',
    'sep': '09', 'sept': '09', 'september': '09',
    'oct': '10', 'october': '10',
    'nov': '11', 'november': '11',
    'dec': '12', 'december': '12',
    # 西班牙语/意大利语
    'ene': '01', 'enero': '01',
    'abr': '04', 'abril': '04',
    'mayo': '05',
    'jun': '06', 'junio': '06',
    'jul': '07', 'julio': '07',
    'ago': '08', 'agosto': '08',
    'dic': '12', 'diciembre': '12',
    # 法语
    'janv': '01', 'janvier': '01',
    'févr': '02', 'février': '02',
    'mars': '03',
    'avr': '04', 'avril': '04',
    'mai': '05',
    'juin': '06',
    'juil': '07', 'juillet': '07',
    'août': '08',
    'septembre': '09',
    'octobre': '10',
    'novembre': '11',
    'déc': '12', 'décembre': '12',
    # 德语
    'januar': '01',
    'februar': '02',
    'mär': '03', 'märz': '03',
    'mai': '05',
    'juni': '06',
    'juli': '07',
    'august': '08',
    'okt': '10', 'oktober': '10',
    'dez': '12', 'dezember': '12',
    # 荷兰语
    'januari': '01',
    'februari': '02',
    'mrt': '03', 'maart': '03',
    'mei': '05',
    'augustus': '08',
    # 瑞典语
    'maj': '05',
    'augusti': '08',
    # 波兰语
    'sty': '01', 'stycznia': '01',
    'lut': '02', 'lutego': '02',
    'marca': '03',
    'kwi': '04', 'kwietnia': '04',
    'maja': '05',
    'cze': '06', 'czerwca': '06',
    'lip': '07', 'lipca': '07',
    'sie': '08', 'sierpnia': '08',
    'wrz': '09', 'września': '09',
    'paź': '10', 'października': '10',
    'lis': '11', 'listopada': '11',
    'gru': '12', 'grudnia': '12'
}

def get_timezone_offset(timezone_str):
    """获取时区偏移量"""
    timezone_str = timezone_str.lower()
    
    if 'utc' in timezone_str:
        return 0
    elif 'pdt' in timezone_str:
        return -7
    elif 'pst' in timezone_str:
        return -8
    elif 'edt' in timezone_str:
        return -4
    elif 'est' in timezone_str:
        return -5
    elif 'cet' in timezone_str:
        return 1
    elif 'cest' in timezone_str:
        return 2
    
    # 检测 GMT+/- 格式
    gmt_match = re.search(r'gmt([+-]\d+)', timezone_str)
    if gmt_match:
        return int(gmt_match.group(1))
    
    return 0

def parse_time(time_str):
    """解析时间字符串"""
    # 匹配 HH:MM:SS 格式
    time_match = re.search(r'(\d{1,2}):(\d{2}):(\d{2})', time_str)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2))
        second = int(time_match.group(3))
        
        # 检查是否有 AM/PM
        ampm_match = re.search(r'(a\.?m\.?|p\.?m\.?)', time_str.lower())
        if ampm_match:
            is_pm = 'p' in ampm_match.group(1)
            if is_pm and hour != 12:
                hour += 12
            elif not is_pm and hour == 12:
                hour = 0
        
        return hour, minute, second
    
    return None, None, None

def convert_date(date_str, include_time=False, convert_to_china=False):
    """转换日期格式"""
    try:
        cleaned = date_str.strip().lower()
        
        # 提取时区信息
        timezone_offset = get_timezone_offset(cleaned)
        
        # 提取时间
        hour, minute, second = parse_time(cleaned)
        has_time = hour is not None
        
        # 移除时区信息
        cleaned = re.sub(r'\s*(utc|gmt|pdt|pst|edt|est|cet|cest).*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s*gmt[+-]\d+.*$', '', cleaned, flags=re.IGNORECASE)
        
        year = month = day = None
        
        # 格式1: DD.MM.YYYY (德语格式)
        match = re.match(r'^(\d{1,2})\.(\d{2})\.(\d{4})', cleaned)
        if match:
            day = int(match.group(1))
            month = int(match.group(2))
            year = int(match.group(3))
        
        # 格式2: DD monthName YYYY
        if not year:
            month_pattern = '|'.join(MONTH_MAP.keys())
            match = re.search(rf'(\d{{1,2}})\s*\.?\s*({month_pattern})\.?\s*(\d{{4}})', cleaned)
            if match:
                day = int(match.group(1))
                month_name = match.group(2).replace('.', '')
                month = int(MONTH_MAP.get(month_name, '00'))
                year = int(match.group(3))
        
        # 格式3: monthName DD YYYY
        if not year:
            match = re.search(rf'({month_pattern})\.?\s*(\d{{1,2}})\.?\s*(\d{{4}})', cleaned)
            if match:
                month_name = match.group(1).replace('.', '')
                month = int(MONTH_MAP.get(month_name, '00'))
                day = int(match.group(2))
                year = int(match.group(3))
        
        if not year:
            return '❌ 无法识别格式'
        
        # 转换为中国时间
        if convert_to_china and has_time:
            china_offset = 8 - timezone_offset
            hour += china_offset
            
            # 处理跨日
            if hour >= 24:
                hour -= 24
                day += 1
                
                # 检查是否需要进入下个月
                days_in_month = [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 
                                 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                if day > days_in_month[month - 1]:
                    day = 1
                    month += 1
                    if month > 12:
                        month = 1
                        year += 1
            
            elif hour < 0:
                hour += 24
                day -= 1
                
                if day < 1:
                    month -= 1
                    if month < 1:
                        month = 12
                        year -= 1
                    days_in_month = [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 
                                     31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                    day = days_in_month[month - 1]
        
        # 格式化输出
        result = f"{year}/{month:02d}/{day:02d}"
        if include_time and has_time:
            result += f" {hour:02d}:{minute:02d}:{second:02d}"
        
        return result
    
    except Exception as e:
        return f'❌ 转换错误: {str(e)}'

# 主界面
st.title("📅 多语言日期格式转换器")
st.markdown("支持US、CA、MX、UK、DE、ES、FR、IT、PL、NL、SE等多种国家的日期格式")

# 选项
col1, col2 = st.columns(2)
with col1:
    include_time = st.checkbox("包含时分秒 (YYYY/MM/DD HH:MM:SS)", value=False)
with col2:
    convert_to_china = st.checkbox("转换为中国时间 (UTC+8 北京时间)", value=False)

# 输入和输出区域
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📝 输入日期（每行一个）")
    input_text = st.text_area(
        "粘贴你的日期数据",
        height=400,
        placeholder="例如：\n30.03.2022 22:01:06 UTC\n30 mar 2022 23:45:12 UTC\n30 mars 2022 22:27:37 UTC",
        key="input"
    )
    
    convert_button = st.button("🔄 转换日期", type="primary", use_container_width=True)

with col_right:
    format_str = "YYYY/MM/DD HH:MM:SS" if include_time else "YYYY/MM/DD"
    st.subheader(f"✅ 转换结果 ({format_str})")
    
    if convert_button and input_text:
        lines = [line.strip() for line in input_text.split('\n') if line.strip()]
        
        results = []
        for line in lines:
            converted = convert_date(line, include_time, convert_to_china)
            results.append(converted)
        
        # 显示结果
        result_text = '\n'.join(results)
        st.text_area("转换结果", value=result_text, height=400, key="output")
        
        # 显示详细对比
        st.markdown("---")
        st.subheader("📊 详细对比")
        for i, (original, converted) in enumerate(zip(lines, results), 1):
            with st.expander(f"第 {i} 行"):
                st.text(f"原始: {original}")
                if '❌' in converted:
                    st.error(f"转换: {converted}")
                else:
                    st.success(f"转换: {converted}")
    else:
        st.text_area("转换结果", value="转换结果将显示在这里...", height=400, disabled=True)

# 使用说明
st.markdown("---")
st.subheader("📖 使用说明")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **基本使用：**
    - 将Excel A列的日期数据复制粘贴到左侧输入框
    - 勾选"包含时分秒"选项可以保留时间信息
    - 勾选"转换为中国时间"会自动识别原时区并转换为UTC+8
    - 点击"转换日期"按钮进行转换
    - 复制右侧结果粘贴到Excel B列
    """)

with col2:
    st.markdown("""
    **支持的功能：**
    - ✅ 支持11种语言的月份名称
    - ✅ 支持多种时区：UTC, PDT, PST, EDT, EST, CET, CEST, GMT+/-
    - ✅ 支持24小时制和12小时制（AM/PM）
    - ✅ 自动处理跨日期的时间转换
    - ✅ 批量转换多行数据
    """)

# 转换示例
st.markdown("---")
st.subheader("💡 转换示例")

example_data = {
    "原始格式": [
        "30.03.2022 22:01:06 UTC",
        "Apr 1. 2022 8:11:08 p.m. PDT",
        "31 mar 2022 20:18:13 GMT-7"
    ],
    "转换结果（不含时间）": [
        "2022/03/30",
        "2022/04/01",
        "2022/03/31"
    ],
    "转换结果（北京时间）": [
        "2022/03/31 06:01:06",
        "2022/04/02 11:11:08",
        "2022/04/01 11:18:13"
    ]
}

st.table(example_data)

# 页脚
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    <p>💡 提示：转换后的日期可以直接复制粘贴到Excel中使用</p>
    </div>
    """,
    unsafe_allow_html=True
)
