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

# 2. [로직] 매입등록비
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
def smart_purchase_manager_neulbarun_v48():
    st.set_page_config(page_title="매입매니저 늘바른 by 김희주", layout="wide")
    
    # CSS 스타일: 희주 님 캡처 이미지의 시원한 폰트 크기 반영
    st.markdown("""
    <style>
        html, body, [class*="css"] { font-size: 16px; }
        .main-title { font-size: 2.5rem; font-weight: 800; color: #2ecc71; display: inline-block; }
        .sub-author { font-size: 0.5em; font-weight: 400; color: #888; margin-left: 10px; }
        .big-price { font-size: 2.5rem; font-weight: 900; color: #4dabf7; margin-bottom: 0px; }
        .real-income { font-size: 2.2rem; font-weight: bold; color: #ffffff; }
        .margin-rate { font-size: 3.0rem; font-weight: 900; color: #ff6b6b; }
        .section-header { font-size: 1.2rem; font-weight: bold; border-left: 5px solid #2ecc71; padding-left: 10px; margin-top: 20px; }
        .detail-table { width: 100%; border-collapse: collapse; font-size: 1.1rem; color: #eee; }
        .detail-table td { padding: 12px; border-bottom: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

    # 1=10,000 자동 변환 로직
    def smart_unit_converter(key):
        val = st.session_state[key]
        if 0 < val <= 5000: 
            st.session_state[key] = int(val * 10000)

    st.markdown('<div class="main-title">매입매니저 늘바른 <span class="sub-author">by 김희주</span></div>', unsafe_allow_html=True)

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
        
        COST_AD, COST_DEPOSIT, COST_POLISH_VAT = 270000, 200000, 132000 
        raw_check = st.radio("성능비 (VAT포함)", [44000, 66000], horizontal=True)
        cost_transport = st.selectbox("교통비 (비과세)", [30000, 50000, 80000, 130000, 170000, 200000])
        
        # 버튼 10,000원씩 오르내림 & 직접입력 변환
        in_dent = st.number_input("판금/도색", step=10000, key='in_dent', on_change=smart_unit_converter, args=('in_dent',), format="%d")
        in_wheel = st.number_input("휠/타이어", step=10000, key='in_wheel', on_change=smart_unit_converter, args=('in_wheel',), format="%d")
        in_etc = st.number_input("기타비용", step=10000, key='in_etc', on_change=smart_unit_converter, args=('in_etc',), format="%d")

        cost_dent_vat = int(in_dent * 1.1)
        cost_wheel_vat = int(in_wheel * 1.1)
        cost_etc_vat = int(in_etc * 1.1)
        fixed_prep_costs = int(cost_transport + cost_dent_vat + cost_wheel_vat + cost_etc_vat + raw_check + COST_AD + COST_POLISH_VAT + COST_DEPOSIT)

    # 수익률 5% 역산 로직
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

    with right_col:
        st.markdown("<div class='section-header'>입찰 금액 결정</div>", unsafe_allow_html=True)
        st.markdown(f"**순수이익 5% 맞춤 매입가 (이자 1.5% 반영)**")
        st.markdown(f"<div class='big-price'>{int(guide_bid):,} 원</div>", unsafe_allow_html=True)
        st.write("")
        my_bid = st.number_input("실제 입찰가 입력", value=int(guide_bid), step=10000, format="%d", label_visibility="collapsed")

    st.markdown("---")

    # 결과값 계산 (강제 정수화)
    res_fee = int(get_auction_fee(my_bid, p_route))
    res_reg = int(get_reg_cost(my_bid, p_type))
    res_interest = int(my_bid * 0.015) 
    total_cost_final = int(my_bid + res_fee + res_reg + res_interest + fixed_prep_costs)
    real_income = int(sales_price - total_cost_final)
    real_margin_rate = (real_income / my_bid * 100) if my_bid > 0 else 0

    c_final1, c_final2 = st.columns(2)
    with c_final1:
        st.markdown("<div style='text-align:center;'>예상 순수익</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center;' class='real-income'>{int(real_income):,} 원</div>", unsafe_allow_html=True)
    with c_final2:
        st.markdown("<div style='text-align:center;'>실질 수익률</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center;' class='margin-rate'>{real_margin_rate:.2f} %</div>", unsafe_allow_html=True)

    # -----------------------------------------------------------
    # [희주 님 캡처 이미지 기반] 상세 견적 및 복사 레이아웃 복구
    # -----------------------------------------------------------
    with st.expander("📄 상세 견적 및 복사 (펼치기)", expanded=True):
        d_col1, d_col2 = st.columns([1, 1], gap="medium")
        with d_col1:
            st.markdown("▼ 상세 내역 (확인용)")
            st.markdown(f"""
            <table class='detail-table'>
                <tr><td><b>판매가</b></td><td align='right'><b>{int(sales_price):,} 원</b></td></tr>
                <tr><td><b>매입가</b></td><td align='right' style='color:#4dabf7;'><b>{int(my_bid):,} 원</b></td></tr>
                <tr><td>총 소요원가</td><td align='right'>{int(total_cost_final):,} 원</td></tr>
                <tr><td colspan='2' style='border-bottom: 2px solid #666;'></td></tr>
                <tr><td>예상이익률</td><td align='right' style='color:#ff6b6b;'>{real_margin_rate:.2f} %</td></tr>
                <tr><td>실소득액</td><td align='right'>{int(real_income):,} 원</td></tr>
                <tr><td colspan='2' style='border-bottom: 2px solid #666;'></td></tr>
                <tr><td>교통비</td><td align='right'>{int(cost_transport):,} 원</td></tr>
                <tr><td>판금/도색</td><td align='right'>{int(cost_dent_vat):,} 원</td></tr>
                <tr><td>휠/타이어</td><td align='right'>{int(cost_wheel_vat):,} 원</td></tr>
                <tr><td>기타비용</td><td align='right'>{int(cost_etc_vat):,} 원</td></tr>
                <tr><td>매입등록비</td><td align='right'>{int(res_reg):,} 원</td></tr>
                <tr><td>낙찰수수료</td><td align='right'>{int(res_fee):,} 원</td></tr>
            </table>
            """, unsafe_allow_html=True)
        with d_col2:
            st.markdown("▼ 복사 전용 텍스트 (우측상단 아이콘 클릭)")
            copy_text = f"판매가  : {int(sales_price):,} 원\n매입가  : {int(my_bid):,} 원\n예상이익률 : {real_margin_rate:.2f} %\n실소득액  : {int(real_income):,} 원\n----------------------------\n교통비   : {int(cost_transport):,} 원\n판금/도색 : {int(cost_dent_vat):,} 원\n휠/타이어 : {int(cost_wheel_vat):,} 원\n기타비용  : {int(cost_etc_vat):,} 원\n매입등록비 : {int(res_reg):,} 원\n낙찰수수료 : {int(res_fee):,} 원"
            st.code(copy_text, language="text")

if __name__ == "__main__":
    smart_purchase_manager_neulbarun_v48()
