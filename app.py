import streamlit as st
import math

# 1. [로직] 낙찰수수료 (수정 없음)
def get_auction_fee(price, route):
    if route == "셀프":
        if price <= 1000000: return 75000
        elif price <= 5000000: return 185000
        elif price <= 10000000: return 245000
        elif price <= 20000000: return 250000
        elif price <= 30000000: return 250000
        else: return 360000
    elif route == "제로":
        if price <= 1000000: return 140000
        elif price <= 5000000: return 300000
        elif price <= 10000000: return 365000
        elif price <= 15000000: return 365000
        elif price <= 30000000: return 395000
        elif price <= 40000000: return 475000
        else: return 505000
    else: return 0

# 2. [로직] 매입등록비
def get_reg_cost(bid_price, p_type):
    threshold = 28500001
    rate = 0.0105
    if p_type == "개인":
        if bid_price >= threshold: return int(bid_price * rate)
        else: return 0
    else:
        supply_price = bid_price / 1.1
        if supply_price >= threshold: return int(supply_price * rate)
        else: return 0

def smart_purchase_manager_neulbarun_v23():
    st.set_page_config(page_title="매입매니저 늘바른 by 김희주", layout="wide")
    
    # CSS 스타일 (생략 - 이전 버전과 동일)
    st.markdown("""<style> .main-title { font-size: 2rem; font-weight: 800; color: #2ecc71; } .big-price { font-size: 2.2rem; font-weight: 900; color: #4dabf7; } .section-header { font-size: 1.1rem; font-weight: bold; border-left: 4px solid #2ecc71; padding-left: 10px; } </style>""", unsafe_allow_html=True)

    if 'in_dent' not in st.session_state: st.session_state['in_dent'] = 0
    if 'in_wheel' not in st.session_state: st.session_state['in_wheel'] = 0
    if 'in_etc' not in st.session_state: st.session_state['in_etc'] = 0

    def smart_unit_converter(key):
        val = st.session_state[key]
        if 0 < val <= 20000: st.session_state[key] = val * 10000

    st.markdown('<div class="main-title">매입매니저 늘바른 <span style="font-size:0.5em; color:#888;">by 김희주</span></div>', unsafe_allow_html=True)

    # 입력창 (판매가, 매입유형, 루트)
    col1, col2, col3 = st.columns([1.5, 1, 1])
    with col1:
        sales_price = st.number_input("판매 예정가 (만원)", value=3500, step=10) * 10000
    with col2:
        p_type = st.radio("매입유형", ["개인", "사업자"])
    with col3:
        p_route = st.selectbox("매입루트", ["셀프", "제로", "개인거래"])

    # 상품화 비용 계산
    COST_AD, COST_DEPOSIT, COST_POLISH_VAT = 270000, 200000, int(120000 * 1.1)
    raw_check = st.radio("성능비", [44000, 66000], horizontal=True)
    cost_transport = st.selectbox("교통비", [30000, 50000, 80000, 130000, 170000, 200000])
    in_dent = st.number_input("판금/도색", key='in_dent', on_change=smart_unit_converter, args=('in_dent',))
    in_wheel = st.number_input("휠/타이어", key='in_wheel', on_change=smart_unit_converter, args=('in_wheel',))
    in_etc = st.number_input("기타비용", key='in_etc', on_change=smart_unit_converter, args=('in_etc',))

    total_prep_vat = cost_transport + int(in_dent*1.1) + int(in_wheel*1.1) + int(in_etc*1.1) + raw_check + COST_AD + COST_POLISH_VAT + COST_DEPOSIT

    # -----------------------------------------------------------
    # [수정] 정밀 역산 로직 (1,000원 단위 정밀 계산)
    # -----------------------------------------------------------
    target_margin_rate = 0.05 
    guide_bid = 0
    
    # 1,000원 단위로 촘촘하게 역산하여 수수료 차이를 확실히 반영
    for test_bid in range(sales_price, 0, -1000): 
        t_fee = get_auction_fee(test_bid, p_route)
        t_reg = get_reg_cost(test_bid, p_type)
        t_interest = int(test_bid * 0.015) 
        
        dealer_revenue = (sales_price - test_bid - t_fee) / 1.1
        current_real_income = int(dealer_revenue - (total_prep_vat - t_fee + t_reg + t_interest))
        
        if test_bid > 0 and (current_real_income / test_bid) >= target_margin_rate:
            guide_bid = test_bid
            break
            
    # 최종 노출만 만원 단위 올림
    if guide_bid > 0: guide_bid = math.ceil(guide_bid / 10000) * 10000

    # 결과 출력 및 상세내역 (이전과 동일, 이자 노출 제외)
    # ... (중략) ...
