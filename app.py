import streamlit as st
import math

# 1. [로직] 낙찰수수료 (희주 님의 고정 원가표)
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

# 2. [로직] 매입등록비 (정수 처리 강화)
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
def smart_purchase_manager_neulbarun_v35():
    st.set_page_config(page_title="매입매니저 늘바른 by 김희주", layout="wide")
    
    st.markdown("""<style> .main-title { font-size: 2rem; font-weight: 800; color: #2ecc71; } .big-price { font-size: 2.2rem; font-weight: 900; color: #4dabf7; } .section-header { font-size: 1.1rem; font-weight: bold; border-left: 4px solid #2ecc71; padding-left: 10px; margin-top: 20px; } .detail-table { width: 100%; border-collapse: collapse; } .detail-table td { padding: 8px; border-bottom: 1px solid #555; } </style>""", unsafe_allow_html=True)

    if 'in_dent' not in st.session_state: st.session_state['in_dent'] = 0
    if 'in_wheel' not in st.session_state: st.session_state['in_wheel'] = 0
    if 'in_etc' not in st.session_state: st.session_state['in_etc'] = 0

    def smart_unit_converter(key):
        val = st.session_state[key]
        if 0 < val <= 20000: st.session_state[key] = int(val * 10000)

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
        st.markdown("<div class='section-header'>상품화 비용 입력 (세전)</div>", unsafe_allow_html=True)
        COST_AD, COST_DEPOSIT, COST_POLISH_VAT = 270000, 200000, int(120000 * 1.1)
        raw_check = st.radio("성능비", [44000, 66000], horizontal=True)
        cost_transport = st.selectbox("교통비", [30000, 50000, 80000, 130000, 170000, 200000])
        in_dent = st.number_input("판금/도색", key='in_dent', on_change=smart_unit_converter, args=('in_dent',))
        in_wheel = st.number_input("휠/타이어", key='in_wheel', on_change=smart_unit_converter, args=('in_wheel',))
        in_etc = st.number_input("기타비용", key='in_etc', on_change=smart_unit_converter, args=('in_etc',))

        cost_dent_vat = int(in_dent * 1.1)
        cost_wheel_vat = int(in_wheel * 1.1)
        cost_etc_vat = int(in_etc * 1.1)
        # 입금비 포함 모든 고정비 합산 (수수료 제외)
        fixed_prep_costs = int(cost_transport + cost_dent_vat + cost_wheel_vat + cost_etc_vat + raw_check + COST_AD + COST_POLISH_VAT + COST_DEPOSIT)

    # -----------------------------------------------------------
    # [수정] 수수료-매입가 1:1 대응 원칙 (소수점 원 박멸)
    # -----------------------------------------------------------
    target_margin_rate = 0.05 
    guide_bid = 0
    
    # 1,000원 단위로 촘촘하게 역산
    for test_bid in range(sales_price, 0, -1000): 
        current_fee = int(get_auction_fee(test_bid, p_route)) # 선택한 루트의 고정 원가 낙찰수수료]
        t_reg = get_reg_cost(test_bid, p_type)
        t_interest = int(test_bid * 0.015) # 금융이자 1.5%
        
        # [핵심 수식] 판매가에서 매입가와 수수료를 뺀 후 부가세를 나눔
        # 이렇게 해야 수수료 1원이 변하면 매입가도 1원 단위로 정확히 반응함
        net_profit_base = int((sales_price - test_bid - current_fee) / 1.1)
        current_real_income = int(net_profit_base - (fixed_prep_costs - current_fee - COST_AD - raw_check) - t_reg - t_interest)
        
        if test_bid > 0 and (current_real_income / test_bid) >= target_margin_rate:
            guide_bid = int(test_bid)
            break
            
    # 최종 결과만 만원 단위 올림
    if guide_bid > 0: guide_bid = int(math.ceil(guide_bid / 10000) * 10000)

    # 세션 상태 업데이트
    if 'prev_guide_bid' not in st.session_state: st.session_state['prev_guide_bid'] = -1
    if guide_bid != st.session_state['prev_guide_bid']:
        st.session_state['my_bid_input'] = guide_bid
        st.session_state['prev_guide_bid'] = guide_bid

    with right_col:
        st.markdown("<div class='section-header'>입찰 금액 결정</div>", unsafe_allow_html=True)
        st.markdown(f"**수익률 5% 맞춤 매입가 (이자 1.5% 반영)**")
        st.markdown(f"<div class='big-price'>{guide_bid:,} 원</div>", unsafe_allow_html=True)
        st.write("")
        my_bid = st.number_input("실제 입찰가 입력", step=10000, format="%d", label_visibility="collapsed", key='my_bid_input', on_change=smart_unit_converter, args=('my_bid_input',))

    st.markdown("---")

    # 결과 출력
    res_fee = int(get_auction_fee(my_bid, p_route))
    res_reg = get_reg_cost(my_bid, p_type)
    res_interest = int(my_bid * 0.015) 
    
    final_profit = int((sales_price - my_bid - res_fee) / 1.1)
    real_income = int(final_profit - (fixed_prep_costs - res_fee - COST_AD - raw_check) - res_reg - res_interest)
    real_margin_rate = (real_income / my_bid * 100) if my_bid > 0 else 0

    c_final1, c_final2 = st.columns(2)
    with c_final1:
        st.markdown("<div style='text-align:center;'>예상 실소득액</div>", unsafe_allow_html=True)
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
                <tr><td>판매가</td><td align='right'>{sales_price:,} 원</td></tr>
                <tr><td>매입가</td><td align='right' style='color:#4dabf7;'>{my_bid:,} 원</td></tr>
                <tr><td>입금비(비과세)</td><td align='right'>{COST_DEPOSIT:,} 원</td></tr>
                <tr><td>교통비(비과세)</td><td align='right'>{cost_transport:,} 원</td></tr>
                <tr><td>판금/도색(VAT)</td><td align='right'>{cost_dent_vat:,} 원</td></tr>
                <tr><td>휠/타이어(VAT)</td><td align='right'>{cost_wheel_vat:,} 원</td></tr>
                <tr><td>매입등록비</td><td align='right'>{res_reg:,} 원</td></tr>
                <tr><td>낙찰수수료</td><td align='right'>{res_fee:,} 원</td></tr>
            </table>
            """, unsafe_allow_html=True)
        with d_col2:
            st.caption("▼ 복사 전용 텍스트")
            copy_text = f"판매가: {sales_price:,}원\n매입가: {my_bid:,}원\n수익률: {real_margin_rate:.2f}%\n실소득: {real_income:,}원\n-----------------\n입금비: {COST_DEPOSIT:,}원\n교통비: {cost_transport:,}원\n판금도색: {cost_dent_vat:,}원\n휠타이어: {cost_wheel_vat:,}원\n매입등록: {res_reg:,}원\n낙찰수수: {res_fee:,}원"
            st.code(copy_text, language="text")

if __name__ == "__main__":
    smart_purchase_manager_neulbarun_v35()
