import streamlit as st
import math

# 1. [로직] 낙찰수수료
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

# 2. [로직] 매입등록비 (비과세)
def get_reg_cost(bid_price, p_type):
    threshold = 28500001
    rate = 0.0105
    if p_type == "개인":
        if bid_price >= threshold: return int(bid_price * rate)
        else: return 0
    else:
        supply_price = int(bid_price / 1.1)
        if supply_price >= threshold: return int(supply_price * rate)
        else: return 0

# 3. 메인 앱
def smart_purchase_manager_neulbarun_v41():
    st.set_page_config(page_title="매입매니저 늘바른 by 김희주", layout="wide")
    
    st.markdown("""<style> .main-title { font-size: 2rem; font-weight: 800; color: #2ecc71; } .big-price { font-size: 2.2rem; font-weight: 900; color: #4dabf7; } .section-header { font-size: 1.1rem; font-weight: bold; border-left: 4px solid #2ecc71; padding-left: 10px; margin-top: 20px; } .detail-table { width: 100%; border-collapse: collapse; } .detail-table td { padding: 8px; border-bottom: 1px solid #555; } </style>""", unsafe_allow_html=True)

    st.markdown('<div class="main-title">매입매니저 늘바른 <span style="font-size:0.5em; color:#888;">by 김희주</span></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1.5, 1, 1])
    with col1:
        sales_input = st.number_input("판매 예정가 (만원)", value=3500, step=10, format="%d")
        sales_price = int(sales_input * 10000)
    with col2:
        p_type = st.radio("매입유형", ["개인", "사업자"])
    with col3:
        p_route = st.selectbox("매입루트", ["셀프", "제로", "개인거래"])

    st.markdown("---")

    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        st.markdown("<div class='section-header'>상품화 비용 입력</div>", unsafe_allow_html=True)
        st.info("※ 광고(27만), 광택(13.2만), 입금(20만) 자동 포함")
        
        COST_AD, COST_DEPOSIT, COST_POLISH_VAT = 270000, 200000, 132000 # 광택비 13.2만 고정
        raw_check = st.radio("성능비 (VAT포함)", [44000, 66000], horizontal=True)
        cost_transport = st.selectbox("교통비 (비과세)", [30000, 50000, 80000, 130000, 170000, 200000])
        
        # [교정] 1 입력 시 만 원으로 자동 계산되도록 입력값만 받고 계산 시 만 원을 곱함
        # step=1로 설정하여 +,- 버튼 클릭 시 1씩(만 원씩) 변화
        in_dent_units = st.number_input("판금/도색 (단위: 만원)", value=0, step=1, format="%d")
        in_wheel_units = st.number_input("휠/타이어 (단위: 만원)", value=0, step=1, format="%d")
        in_etc_units = st.number_input("기타비용 (단위: 만원)", value=0, step=1, format="%d")

        # 실제 금액 변환 및 VAT 합산
        cost_dent_vat = int(in_dent_units * 10000 * 1.1)
        cost_wheel_vat = int(in_wheel_units * 10000 * 1.1)
        cost_etc_vat = int(in_etc_units * 10000 * 1.1)
        
        fixed_prep_costs = int(cost_transport + cost_dent_vat + cost_wheel_vat + cost_etc_vat + raw_check + COST_AD + COST_POLISH_VAT + COST_DEPOSIT)

    # -----------------------------------------------------------
    # [희주 님 공식] 판매가 - 모든 원가 = 순수익 5% 역산
    # -----------------------------------------------------------
    target_margin_rate = 0.05 
    guide_bid = 0
    
    for test_bid in range(sales_price, 0, -1000): 
        t_fee = int(get_auction_fee(test_bid, p_route))
        t_reg = int(get_reg_cost(test_bid, p_type))
        t_interest = int(test_bid * 0.015) 
        
        total_cost = test_bid + t_fee + t_reg + t_interest + fixed_prep_costs
        net_profit = sales_price - total_cost
        
        if test_bid > 0 and (net_profit / test_bid) >= target_margin_rate:
            guide_bid = int(test_bid)
            break
            
    if guide_bid > 0: guide_bid = int(math.ceil(guide_bid / 10000) * 10000)

    # 입찰가 필드 업데이트
    if 'my_bid_input' not in st.session_state or guide_bid != st.session_state.get('prev_guide'):
        st.session_state['my_bid_input'] = guide_bid
        st.session_state['prev_guide'] = guide_bid

    with right_col:
        st.markdown("<div class='section-header'>입찰 금액 결정</div>", unsafe_allow_html=True)
        st.markdown(f"**순수이익 5% 맞춤 매입가 (이자 1.5% 반영)**")
        st.markdown(f"<div class='big-price'>{guide_bid:,} 원</div>", unsafe_allow_html=True)
        st.write("")
        my_bid = st.number_input("실제 입찰가 입력", value=int(st.session_state['my_bid_input']), step=10000, format="%d", label_visibility="collapsed")

    st.markdown("---")

    # 결과 출력
    res_fee = int(get_auction_fee(my_bid, p_route))
    res_reg = int(get_reg_cost(my_bid, p_type))
    res_interest = int(my_bid * 0.015) 
    
    total_cost_final = int(my_bid + res_fee + res_reg + res_interest + fixed_prep_costs)
    real_income = int(sales_price - total_cost_final)
    real_margin_rate = (real_income / my_bid * 100) if my_bid > 0 else 0

    c_final1, c_final2 = st.columns(2)
    with c_final1:
        st.markdown("<div style='text-align:center;'>예상 실소득액 (순수이익)</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center;' class='real-income'>{real_income:,} 원</div>", unsafe_allow_html=True)
    with c_final2:
        st.markdown("<div style='text-align:center;'>실질 수익률 (매입가 대비)</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center;' class='margin-rate'>{real_margin_rate:.2f} %</div>", unsafe_allow_html=True)

    with st.expander("🧾 상세 내역 및 복사 (펼치기)", expanded=True):
        d_col1, d_col2 = st.columns([1, 1], gap="medium")
        with d_col1:
            st.caption("▼ 상세 내역 (확인용)")
            st.markdown(f"""
            <table class='detail-table'>
                <tr><td>판매가</td><td align='right'>{int(sales_price):,} 원</td></tr>
                <tr><td>매입가</td><td align='right' style='color:#4dabf7;'>{int(my_bid):,} 원</td></tr>
                <tr><td>입금비(비과세)</td><td align='right'>{int(COST_DEPOSIT):,} 원</td></tr>
                <tr><td>낙찰수수료(VAT함)</td><td align='right'>{int(res_fee):,} 원</td></tr>
                <tr><td>매입등록비(비과세)</td><td align='right'>{int(res_reg):,} 원</td></tr>
                <tr><td>상품화비 합계(VAT함)</td><td align='right'>{int(cost_dent_vat + cost_wheel_vat + cost_etc_vat):,} 원</td></tr>
            </table>
            """, unsafe_allow_html=True)
        with d_col2:
            st.caption("▼ 복사 전용 텍스트")
            copy_text = f"판매가: {int(sales_price):,}원\n매입가: {int(my_bid):,}원\n수익률: {real_margin_rate:.2f}%\n순수익: {int(real_income):,}원\n-----------------\n입금비(비과세): {int(COST_DEPOSIT):,}원\n교통비(비과세): {int(cost_transport):,}원\n매입등록(비과세): {int(res_reg):,}원\n낙찰수수(VAT함): {int(res_fee):,}원"
            st.code(copy_text, language="text")

if __name__ == "__main__":
    smart_purchase_manager_neulbarun_v41()
