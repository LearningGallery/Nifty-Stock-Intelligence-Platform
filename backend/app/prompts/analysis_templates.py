"""
Analysis Output Templates
"""

COMPREHENSIVE_ANALYSIS_TEMPLATE = """
# 📊 {stock_symbol} - Comprehensive Stock Analysis

**Generated on:** {timestamp}  
**Analysis Type:** {analysis_type}  
**Timeframe:** {timeframe}

---

## 🎯 OVERALL RECOMMENDATION

**Recommendation:** {recommendation}  
**Confidence Level:** {confidence_level} ({confidence_percentage}%)  
**Risk Level:** {risk_level}

---

## ✅ PROS (Reasons to Consider)

{pros_list}

---

## ❌ CONS (Risks & Concerns)

{cons_list}

---

## 📈 TIMEFRAME-BASED TARGETS

### Short-Term (1-3 months)
- **Entry Point:** ₹{short_entry}
- **Target 1:** ₹{short_target1} ({short_upside1}% upside)
- **Target 2:** ₹{short_target2} ({short_upside2}% upside)
- **Stop Loss:** ₹{short_stoploss} ({short_downside}% downside)
- **Risk-Reward Ratio:** {short_rr_ratio}

### Long-Term (6-12 months)
- **Entry Range:** ₹{long_entry_low} - ₹{long_entry_high}
- **Target:** ₹{long_target} ({long_upside}% upside)
- **Stop Loss:** ₹{long_stoploss} ({long_downside}% downside)
- **Investment Thesis:** {investment_thesis}

---

## 📊 TECHNICAL SIGNALS

**Overall Trend:** {trend}  
**Technical Score:** {technical_score}/10

### Key Indicators:
- **Moving Averages:** {ma_signal}
- **RSI (14):** {rsi_value} - {rsi_signal}
- **MACD:** {macd_signal}
- **Volume:** {volume_signal}

### Support & Resistance:
- **Key Support:** ₹{support_levels}
- **Key Resistance:** ₹{resistance_levels}

### Recent Crossovers:
{crossovers}

---

## 💼 FUNDAMENTAL SNAPSHOT

**Fundamental Score:** {fundamental_score}/10

### Valuation Metrics:
- **P/E Ratio:** {pe_ratio} (Industry Avg: {industry_pe})
- **P/B Ratio:** {pb_ratio}
- **Debt/Equity:** {debt_equity}

### Profitability:
- **ROE:** {roe}%
- **Net Profit Margin:** {npm}%
- **Revenue Growth (YoY):** {revenue_growth}%

### Ownership:
- **Promoter Holding:** {promoter_holding}%
- **Pledged Shares:** {pledged_pct}%

---

## 📰 NEWS & SENTIMENT

**Sentiment Score:** {sentiment_score}/10  
**Overall Sentiment:** {sentiment}

### Recent Developments:
{news_summary}

### Latest Headlines:
{recent_headlines}

---

## ⚠️ RISK FACTORS TO MONITOR

{risk_factors}

---

## 🔔 ACTION ITEMS

{action_items}

---

## 📌 Data Sources
{data_sources}

---

{disclaimer}
"""

---

QUICK_SNAPSHOT_TEMPLATE = """
## 📊 {stock_symbol} - Quick Snapshot

**Current Price:** ₹{current_price} ({change_pct}%)  
**Recommendation:** {recommendation}  
**Signal:** {signal}

**Key Highlight:** {key_highlight}

**Watch Out For:** {key_risk}

{disclaimer_short}
"""
