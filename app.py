import streamlit as st
import math

# -----------------------------------------------------------
# 1. [로직] 낙찰수수료 (기본 유지)
# -----------------------------------------------------------
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

# -----------------------------------------------------------
# 2. [로직] 매입등록비
# -----------------------------------------------------------
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

# -----------------------------------------------------------
# 3. 메인 앱 (Project: Smart Purchase Manager)
# -----------------------------------------------------------
def smart_purchase_manager():
    st.set_page_config(page_title="매입 매니저 by 김희주", layout="wide")
    
    st.markdown("""
    <style>
        .main-title { font-size: 2.2rem; font-weight: 900; color: #2ecc71; margin-bottom: 20px; }
        .section-header { font-size: 1.1rem; font-weight: bold; border-left: 4px solid #2ecc71; padding-left: 10px; margin: 20px 0 10px 0; }
        .result-box { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #dee2e6; text-align: center; }
        .highlight-price { font-size: 2rem; font-weight: 800; color: #e74c3c; }
        @media (prefers-color-scheme: dark) { .result-box { background-color: #262730; border: 1px solid #464646; } }
    </style>
    """, unsafe_allow_html=True)

    # 세션 상태 초기화
    if 'my_bid' not in st.session_state: st.session_state['my_bid'] = 0

    def convert_unit(key):
        if 0 < st.session_state[key] <= 20000:
            st.session_state[key] *= 10000

    st.markdown("<div class='main-title'>🚗 매입 매니저 v1.0</div>", unsafe_allow_html=True)

    # 상단 설정
    col1, col2, col3 = st.columns([1.5, 1, 1])
    with col1:
        sales_input = st.number_input("예상 판매가 (만원)", value=3000, step=10)
        sales_price = sales_input * 10000
    with col2: p_type = st.radio("매입 유형", ["개인", "사업자"])
    with col3: p_route = st.selectbox("매입 루트", ["셀프", "제로", "개인거래"])

    st.markdown("---")

    left, right = st.columns(2, gap="large")

    with left:
        st.markdown("<div class='section-header'>🛠️ 상품화 비용 (공급가 입력)</div>", unsafe_allow_html=True)
        st.caption("입력하신 금액에 부가세 10%가 자동으로 합산되어 원가에 반영됩니다.")
        
        # 입력은 공급가로, 계산은 부가세 포함으로
        in_perf = st.radio("성능점검비", [40000, 60000], horizontal=True)
        in_trans = st.selectbox("교통비", [30000, 50000, 80000, 130000, 170000, 200000])
        
        in_dent = st.number_input("판금/도색", key='in_dent', on_change=convert_unit, args=('in_dent',))
        in_wheel = st.number_input("휠/타이어", key='in_wheel', on_change=convert_unit, args=('in_wheel',))
        in_etc = st.number_input("기타 정비", key='in_etc', on_change=convert_unit, args=('in_etc',))

        # 고정비 설정 (부가세 포함 처리)
        # 광고 27만(포함), 광택 12만(공급가 기준 -> 13.2만), 입금 6만 삭제
        COST_AD = 270000 
        COST_POLISH = int(120000 * 1.1)
        
        # 합산 (모든 입력값에 1.1 곱함)
        total_prep_cost = int((in_perf + in_trans + in_dent + in_wheel + in_etc) * 1.1) + COST_AD + COST_POLISH

    # 가이드 계산 로직 (실소득률 5% 확보를 위해 타겟 마진율 상향)
    # 금리 1.5% 및 부가세 통합을 고려하여 판매가의 약 7.5%를 공간으로 확보
    target_rate = 0.075
    guide_bid = 0
    temp_start = int(sales_price * (1 - target_rate)) - total_prep_cost
    
    for b in range(temp_start, temp_start - 5000000, -10000):
        f = get_auction_fee(b, p_route)
        r = get_reg_cost(b, p_type)
        i = int(b * 0.015) # 금리 1.5%
        if (b + total_prep_cost + f + r + i) <= (sales_price * 0.94): # 부가세 매입세액 공제 고려한 안전선
            guide_bid = b
            break
    
    # 가이드값 자동 동기화
    if st.session_state.get('last_guide') != guide_bid:
        st.session_state['my_bid'] = guide_bid
        st.session_state['last_guide'] = guide_bid

    with right:
        st.markdown("<div class='section-header'>💰 입찰 결정</div>", unsafe_allow_html=True)
        st.write("권장 매입가 (Margin 5%+) ")
        st.markdown(f"<div class='highlight-price'>{guide_bid:,} 원</div>", unsafe_allow_html=True)
        
        my_bid = st.number_input("최종 입찰금액", key='my_bid', on_change=convert_unit, args=('my_bid',))
        
        # 상세 원가 계산
        res_fee = get_auction_fee(my_bid, p_route)
        res_reg = get_reg_cost(my_bid, p_type)
        res_interest = int(my_bid * 0.015) # 금리 1.5%
        
        # 실소득 계산 (3.3% 제외 없음)
        # (판매가 - 매입가 - 낙찰수수료) / 1.1 -> 딜러 마진(세전)
        margin_before_prep = (sales_price - my_bid - res_fee) / 1.1
        # 실소득 = 마진 - (나머지 부가세포함 상품화비용 + 등록비 + 이자)
        real_profit = int(margin_before_prep - (total_prep_cost - res_fee + res_reg + res_interest))
        profit_rate = (real_profit / my_bid * 100) if my_bid > 0 else 0

    st.markdown("---")
    
    # 결과 요약
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("예상 실소득 (월급 전)", f"{real_profit:,} 원")
    with c2:
        st.metric("이익률 (매입가 대비)", f"{profit_rate:.2f} %")
    with c3:
        total_out = my_bid + total_prep_cost + res_reg + res_interest
        st.metric("총 투입 원가", f"{total_out:,} 원")

    # 복사용 텍스트
    with st.expander("📝 상세 내역 복사하기"):
        copy_text = f"""[매입 견적서]
판매예정가 : {sales_price:,}원
최종매입가 : {my_bid:,}원
-------------------------
예상이익률 : {profit_rate:.2f}%
예상실소득 : {real_profit:,}원 (금리 1.5% 반영)
-------------------------
상품화(부값포함): {total_prep_cost:,}원
매입등록비 : {res_reg:,}원
낙찰수수료 : {res_fee:,}원
금융이자(1.5%) : {res_interest:,}원"""
        st.code(copy_text, language="text")

if __name__ == "__main__":
    smart_purchase_manager()