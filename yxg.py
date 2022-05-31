# coding:utf-8

total_price = 300
cost_price = 50
wx_op_rate = 0.006
VAT_rate = 0.06  # 增值税率
commission_rate = 0.6  # 提成比率
wx_op_fee = total_price * wx_op_rate  # 微信手续费
addition_fee = (total_price-cost_price) * VAT_rate  # 增值费
pure_business_volume = (total_price-cost_price) * (1-VAT_rate)  # 净营业额度

settlement = pure_business_volume * commission_rate + cost_price - wx_op_fee  # 结算
print('净营业额度', pure_business_volume)
print('结算', settlement)
