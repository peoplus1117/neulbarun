import streamlit as st
import math

# -----------------------------------------------------------
# 1. [로직] 낙찰수수료
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
# 3. 메인 앱
# -----------------------------------------------------------
def smart_purchase_manager_neulbarun_v15():
    st.set_page_config(page_title="매입매니저 늘바른 by 김희주", layout="wide")
    
    st.markdown("""
    <style>
        html, body, [class*="css"] { font-size: 16px; }
        @media (max-width: 600px) { html, body, [class*="css"] { font-size: 14px; } }
        
        .main-title { font-size: clamp(1.5rem, 4vw, 2.5rem); font-weight: 800; color: #2ecc71; display: inline-block; }
        .sub-author { font-size: 0.5em; font-weight: 400; color: #888; margin-left: 10px; }
        
        .big-price { font-size: clamp(1.6rem, 3.5vw, 2.2rem); font-weight: 900; color: #4dabf7; margin-bottom: 0px; }
        .real-income { font-size: clamp(1.4rem, 2.5vw, 1.8rem); font-weight: bold; }
        .margin-rate { font-size: clamp(2.0rem, 4vw, 2.5rem); font-weight: 900; color: #ff6b6b; }
        .input-check { font-size: 0.9rem; color: #2e7d32; font-weight: bold; margin-top: -10px; margin-bottom: 20px; }
        .section-header { font-size: 1.1rem; font-weight: bold; margin-bottom: 10px; border-left: 4px solid #2ecc71; padding-left: 10px; }
        
        .detail-table-container { width: 100%; max-width: 450px; margin: 0 auto; }
        .detail-table { width: 100%; border-collapse: collapse; font-size: clamp(0.9rem, 2.5vw, 1.1rem); }
        .detail-table td { padding: 6px 10px; border-bottom: 1px solid #555; }
        @media (prefers-color-scheme: light) { .detail-table td { border-bottom: 1px solid #ddd; } }
        .detail-label { font-weight: bold; opacity: 0.9; white-space: nowrap; }
        .detail-value { text-align: right; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

    if 'in_dent' not in st.session_state: st.session_state['in_dent'] = 0
    if 'in_wheel' not in st.session_state: st.session_state['in_wheel'] = 0
    if 'in_etc' not in st.session_state: st.session_state['in_etc'] = 0

    def smart_unit_converter(key):
        val = st.session_state[key]
        if 0 < val <= 20000: st.session_state[key] = val * 10000

    st.markdown('<div class="main-title">매입매니저 늘바른 <span class="sub-author">by 김희주</span></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1.5, 1, 1])
    with col1:
        sales_input = st.number_input("판매 예정가 (단위: 만원)", value=3500, step=10, format="%d")
        sales_price = sales_input * 10000
        st.markdown(f"<div class='input-check'>확인: {sales_price:,} 원</div>", unsafe_allow_html=True)
    with col2:
        p_type = st.radio("매입유형", ["개인", "사업자"])
    with col3:
        p_route = st.selectbox("매입루트", ["셀프", "제로", "개인거래"])

    st.markdown("---")

    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        st.markdown("<div class='section-header'>상품화 비용 입력 (공급가)</div>", unsafe_allow_html=True)
        in_perf = st.radio("성능점검비 (VAT포함)", [44000, 66000], horizontal=True)
        in_transport = st.selectbox("교통비", [30000, 50000, 80000, 130000, 170000, 200000])
        
        in_dent = st.number_input("판금/도색", step=10000, format="%d", key='in_dent', on_change=smart_unit_converter, args=('in_dent',))
        in_wheel = st.number_input("휠/타이어", step=10000, format="%d", key='in_wheel', on_change=smart_unit_converter, args=('in_wheel',))
        in_etc = st.number_input("기타비용", step=10000, format="%d", key='in_etc', on_change=smart_unit_converter, args=('in_etc',))

        COST_AD = 270000 
        COST_POLISH = 132000 
        total_prep_vat = int((in_transport + in_dent + in_wheel + in_etc) * 1.1) + in_perf + COST_AD + COST_POLISH
        st.caption(f"※ 광고(27만), 광택(13.2만) 포함 / 모든 입력값 부가세 10% 가산됨")

    # -----------------------------------------------------------
    # [가이드 로직: 타겟 마진 4% 설정]
    # -----------------------------------------------------------
    # 실소득 4%를 확보하기 위해 판매가의 약 95% 선을 예산으로 잡음 (0.94 -> 0.95로 상향)
    budget_after_margin = int(sales_price * 0.95) 
    guide_bid = 0
    
    start_point = budget_after_margin - total_prep_vat
    for bid in range(start_point, start_point - 5000000, -10000):
        fee = get_auction_fee(bid, p_route)
        reg = get_reg_cost(bid, p_type)
        interest = int(bid * 0.015) 
        if (bid + total_prep_vat + fee + reg + interest) <= budget_after_margin:
            guide_bid = bid
            break
            
    if guide_bid > 0:
        guide_bid = math.ceil(guide_bid / 10000) * 10000

    if 'prev_guide_bid' not in st.session_state: st.session_state['prev_guide_bid'] = -1
    if guide_bid != st.session_state['prev_guide_bid']:
        st.session_state['my_bid_input'] = guide_bid
        st.session_state['prev_guide_bid'] = guide_bid

    with right_col:
        st.markdown("<div class='section-header'>입찰 금액 결정</div>", unsafe_allow_html=True)
        st.markdown("**적정 매입가 (Guide)**")
        st.markdown(f"<div class='big-price'>{guide_bid:,} 원</div>", unsafe_allow_html=True)
        st.write("")
        st.markdown("**▼ 실제 입찰금액 입력**")
        my_bid = st.number_input("입찰가 입력", step=10000, format="%d", label_visibility="collapsed", key='my_bid_input', on_change=smart_unit_converter, args=('my_bid_input',))
        
        bid_ratio = (my_bid / sales_price) * 100 if sales_price > 0 else 0
        st.markdown(f"<div class='input-check' style='text-align:right;'>확인: ({bid_ratio:.1f}%) {my_bid:,} 원</div>", unsafe_allow_html=True)

    st.markdown("---")

    # 결과 계산
    res_fee = get_auction_fee(my_bid, p_route)
    res_reg = get_reg_cost(my_bid, p_type)
    res_interest = int(my_bid * 0.015)
    
    dealer_revenue = (sales_price - my_bid - res_fee) / 1.1
    real_income = int(dealer_revenue - (total_prep_vat - res_fee + res_reg + res_interest))
    real_margin_rate = (real_income / my_bid * 100) if my_bid > 0 else 0
    total_cost = my_bid + total_prep_vat + res_reg + res_interest

    c_final1, c_final2 = st.columns(2)
    with c_final1:
        st.markdown("<div style='text-align:center;'>예상 실소득액</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center;' class='real-income'>{real_income:,} 원</div>", unsafe_allow_html=True)
    with c_final2:
        st.markdown("<div style='text-align:center;'>예상 이익률 (매입가 대비)</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center;' class='margin-rate'>{real_margin_rate:.2f} %</div>", unsafe_allow_html=True)

    st.write("")

    with st.expander("🧾 상세 견적 및 복사 (펼치기)", expanded=True):
        d_col1, d_col2 = st.columns([1, 1], gap="medium")
        with d_col1:
            st.caption("▼ 상세 내역 (확인용)")
            st.markdown(f"""
            <div class='detail-table-container'>
                <table class='detail-table'>
                    <tr><td class='detail-label'>판매가</td><td class='detail-value'>{sales_price:,} 원</td></tr>
                    <tr><td class='detail-label'>매입가</td><td class='detail-value' style='color:#4dabf7;'>{my_bid:,} 원</td></tr>
                    <tr><td class='detail-label'>총 소요원가</td><td class='detail-value' style='color:#aaa;'>{total_cost:,} 원</td></tr>
                    <tr><td colspan='2' style='height:8px; border-bottom:1px dashed #777;'></td></tr>
                    <tr><td class='detail-label'>예상이익률</td><td class='detail-value' style='color:#ff6b6b;'>{real_margin_rate:.2f} %</td></tr>
                    <tr><td class='detail-label'>실소득액</td><td class='detail-value'>{real_income:,} 원</td></tr>
                    <tr><td colspan='2' style='height:8px; border-bottom:1px dashed #777;'></td></tr>
                    <tr><td class='detail-label'>상품화합계(VAT포함)</td><td class='detail-value'>{total_prep_vat:,} 원</td></tr>
                    <tr><td class='detail-label'>매입등록비</td><td class='detail-value'>{res_reg:,} 원</td></tr>
                    <tr><td class='detail-label'>낙찰수수료</td><td class='detail-value'>{res_fee:,} 원</td></tr>
                    <tr><td class='detail-label'>금융이자(1.5%)</td><td class='detail-value'>{res_interest:,} 원</td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
            
        with d_col2:
            st.caption("▼ 복사 전용 텍스트")
            copy_text = f"""판매가   : {sales_price:,} 원
매입가   : {my_bid:,} 원
예상이익률 : {real_margin_rate:.2f} %
실소득액  : {real_income:,} 원
-------------------------
상품화합계 : {total_prep_vat:,} 원
매입등록비 : {res_reg:,} 원
낙찰수수료 : {res_fee:,} 원
금융이자(1.5%) : {res_interest:,} 원"""
            st.code(copy_text, language="text")

if __name__ == "__main__":
    smart_purchase_manager_neulbarun_v15()
