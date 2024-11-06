\ Model GFsavings
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  34.64 compressor_state[0] + 34.64 compressor_state[1]
   + 34.64 compressor_state[2] + 34.64 compressor_state[3]
   + 34.64 compressor_state[4] + 34.64 compressor_state[5]
   + 0 predictedtemplowerupper[5] + 0 predictedtempmed[5]
Subject To
 R0: - 0.0003 htimemed[0] + 9e-10 htimemed^2[0] + tempheatedtomed[0]
   = 2.3445
 R1: 0.0005 ctimemed[0] - 3e-09 ctimemed^2[0] + tempcooledtomed[0]
   = 16.775
 R2: - 0.0003 htimemed[1] + 9e-10 htimemed^2[1] + tempheatedtomed[1]
   = 2.3445
 R3: 0.0005 ctimemed[1] - 3e-09 ctimemed^2[1] + tempcooledtomed[1]
   = 16.775
 R4: - 0.0003 htimemed[2] + 9e-10 htimemed^2[2] + tempheatedtomed[2]
   = 2.3445
 R5: 0.0005 ctimemed[2] - 3e-09 ctimemed^2[2] + tempcooledtomed[2]
   = 16.775
 R6: - 0.0003 htimemed[3] + 9e-10 htimemed^2[3] + tempheatedtomed[3]
   = 2.3445
 R7: 0.0005 ctimemed[3] - 3e-09 ctimemed^2[3] + tempcooledtomed[3]
   = 16.775
 R8: - 0.0003 htimemed[4] + 9e-10 htimemed^2[4] + tempheatedtomed[4]
   = 2.3445
 R9: 0.0005 ctimemed[4] - 3e-09 ctimemed^2[4] + tempcooledtomed[4]
   = 16.775
 R10: - 0.0003 htimemed[5] + 9e-10 htimemed^2[5] + tempheatedtomed[5]
   = 2.3445
 R11: 0.0005 ctimemed[5] - 3e-09 ctimemed^2[5] + tempcooledtomed[5]
   = 16.775
 Tlowererbound[0]: interpolatedtemp[0] >= 2.22
 Tlowererbound[1]: interpolatedtemp[1] >= 2.22
 Tlowererbound[2]: interpolatedtemp[2] >= 2.22
 Tlowererbound[3]: interpolatedtemp[3] >= 2.22
 Tlowererbound[4]: interpolatedtemp[4] >= 2.22
 Tlowererbound[5]: interpolatedtemp[5] >= 2.22
 Tupperbound[0]: interpolatedtemp[0] <= 4.44
 Tupperbound[1]: interpolatedtemp[1] <= 4.44
 Tupperbound[2]: interpolatedtemp[2] <= 4.44
 Tupperbound[3]: interpolatedtemp[3] <= 4.44
 Tupperbound[4]: interpolatedtemp[4] <= 4.44
 Tupperbound[5]: interpolatedtemp[5] <= 4.44
 initial_temp: interpolatedtemp[0] = 3.33
 R25: tempheatedtolu[0] - 0.0001 htimefull[0] + 7e-11 htimefull^2[0]
   = 1.0776
 R26: tempcooledtolu[0] + 0.0052 ctimefull[0] - 4e-07 ctimefull^2[0]
   = 18.248
 R27: tempheatedtolu[1] - 0.0001 htimefull[1] + 7e-11 htimefull^2[1]
   = 1.0776
 R28: tempcooledtolu[1] + 0.0052 ctimefull[1] - 4e-07 ctimefull^2[1]
   = 18.248
 R29: tempheatedtolu[2] - 0.0001 htimefull[2] + 7e-11 htimefull^2[2]
   = 1.0776
 R30: tempcooledtolu[2] + 0.0052 ctimefull[2] - 4e-07 ctimefull^2[2]
   = 18.248
 R31: tempheatedtolu[3] - 0.0001 htimefull[3] + 7e-11 htimefull^2[3]
   = 1.0776
 R32: tempcooledtolu[3] + 0.0052 ctimefull[3] - 4e-07 ctimefull^2[3]
   = 18.248
 R33: tempheatedtolu[4] - 0.0001 htimefull[4] + 7e-11 htimefull^2[4]
   = 1.0776
 R34: tempcooledtolu[4] + 0.0052 ctimefull[4] - 4e-07 ctimefull^2[4]
   = 18.248
 R35: tempheatedtolu[5] - 0.0001 htimefull[5] + 7e-11 htimefull^2[5]
   = 1.0776
 R36: tempcooledtolu[5] + 0.0052 ctimefull[5] - 4e-07 ctimefull^2[5]
   = 18.248
 Futuretemp[0]: - 0.5 predictedtemplowerupper[0] - 0.5 predictedtempmed[0]
   + interpolatedtemp[1] = 0
 Futuretemp[1]: - 0.5 predictedtemplowerupper[1] - 0.5 predictedtempmed[1]
   + interpolatedtemp[2] = 0
 Futuretemp[2]: - 0.5 predictedtemplowerupper[2] - 0.5 predictedtempmed[2]
   + interpolatedtemp[3] = 0
 Futuretemp[3]: - 0.5 predictedtemplowerupper[3] - 0.5 predictedtempmed[3]
   + interpolatedtemp[4] = 0
 Futuretemp[4]: - 0.5 predictedtemplowerupper[4] - 0.5 predictedtempmed[4]
   + interpolatedtemp[5] = 0
 qc0: 692.49 interpolatedtemp[0] + htimemed[0] + [
   - 291.94 interpolatedtemp[0] ^2 ] = 7305
 qc1: 7852.6 interpolatedtemp[0] + ctimemed[0] + [
   - 229.21 interpolatedtemp[0] ^2 ] = 68574
 qc2: 692.49 interpolatedtemp[1] + htimemed[1] + [
   - 291.94 interpolatedtemp[1] ^2 ] = 7305
 qc3: 7852.6 interpolatedtemp[1] + ctimemed[1] + [
   - 229.21 interpolatedtemp[1] ^2 ] = 68574
 qc4: 692.49 interpolatedtemp[2] + htimemed[2] + [
   - 291.94 interpolatedtemp[2] ^2 ] = 7305
 qc5: 7852.6 interpolatedtemp[2] + ctimemed[2] + [
   - 229.21 interpolatedtemp[2] ^2 ] = 68574
 qc6: 692.49 interpolatedtemp[3] + htimemed[3] + [
   - 291.94 interpolatedtemp[3] ^2 ] = 7305
 qc7: 7852.6 interpolatedtemp[3] + ctimemed[3] + [
   - 229.21 interpolatedtemp[3] ^2 ] = 68574
 qc8: 692.49 interpolatedtemp[4] + htimemed[4] + [
   - 291.94 interpolatedtemp[4] ^2 ] = 7305
 qc9: 7852.6 interpolatedtemp[4] + ctimemed[4] + [
   - 229.21 interpolatedtemp[4] ^2 ] = 68574
 qc10: 692.49 interpolatedtemp[5] + htimemed[5] + [
   - 291.94 interpolatedtemp[5] ^2 ] = 7305
 qc11: 7852.6 interpolatedtemp[5] + ctimemed[5] + [
   - 229.21 interpolatedtemp[5] ^2 ] = 68574
 qc12: - 8701.1 interpolatedtemp[0] + htimefull[0] + [
   - 99.057 interpolatedtemp[0] ^2 ] = -7709.8
 qc13: 10142 interpolatedtemp[0] + ctimefull[0] + [
   - 281.28 interpolatedtemp[0] ^2 ] = 97818
 qc14: - 8701.1 interpolatedtemp[1] + htimefull[1] + [
   - 99.057 interpolatedtemp[1] ^2 ] = -7709.8
 qc15: 10142 interpolatedtemp[1] + ctimefull[1] + [
   - 281.28 interpolatedtemp[1] ^2 ] = 97818
 qc16: - 8701.1 interpolatedtemp[2] + htimefull[2] + [
   - 99.057 interpolatedtemp[2] ^2 ] = -7709.8
 qc17: 10142 interpolatedtemp[2] + ctimefull[2] + [
   - 281.28 interpolatedtemp[2] ^2 ] = 97818
 qc18: - 8701.1 interpolatedtemp[3] + htimefull[3] + [
   - 99.057 interpolatedtemp[3] ^2 ] = -7709.8
 qc19: 10142 interpolatedtemp[3] + ctimefull[3] + [
   - 281.28 interpolatedtemp[3] ^2 ] = 97818
 qc20: - 8701.1 interpolatedtemp[4] + htimefull[4] + [
   - 99.057 interpolatedtemp[4] ^2 ] = -7709.8
 qc21: 10142 interpolatedtemp[4] + ctimefull[4] + [
   - 281.28 interpolatedtemp[4] ^2 ] = 97818
 qc22: - 8701.1 interpolatedtemp[5] + htimefull[5] + [
   - 99.057 interpolatedtemp[5] ^2 ] = -7709.8
 qc23: 10142 interpolatedtemp[5] + ctimefull[5] + [
   - 281.28 interpolatedtemp[5] ^2 ] = 97818
 GC2: compressor_state[0] = 0 -> predictedtempmed[0] - tempheatedtomed[0]
   = 0
 GC3: compressor_state[0] = 1 -> predictedtempmed[0] - tempcooledtomed[0]
   = 0
 GC6: compressor_state[1] = 0 -> predictedtempmed[1] - tempheatedtomed[1]
   = 0
 GC7: compressor_state[1] = 1 -> predictedtempmed[1] - tempcooledtomed[1]
   = 0
 GC10: compressor_state[2] = 0 -> predictedtempmed[2] - tempheatedtomed[2]
   = 0
 GC11: compressor_state[2] = 1 -> predictedtempmed[2] - tempcooledtomed[2]
   = 0
 GC14: compressor_state[3] = 0 -> predictedtempmed[3] - tempheatedtomed[3]
   = 0
 GC15: compressor_state[3] = 1 -> predictedtempmed[3] - tempcooledtomed[3]
   = 0
 GC18: compressor_state[4] = 0 -> predictedtempmed[4] - tempheatedtomed[4]
   = 0
 GC19: compressor_state[4] = 1 -> predictedtempmed[4] - tempcooledtomed[4]
   = 0
 GC22: compressor_state[5] = 0 -> predictedtempmed[5] - tempheatedtomed[5]
   = 0
 GC23: compressor_state[5] = 1 -> predictedtempmed[5] - tempcooledtomed[5]
   = 0
 GC26: compressor_state[0] = 0 -> predictedtemplowerupper[0]
   - tempheatedtolu[0] = 0
 GC27: compressor_state[0] = 1 -> predictedtemplowerupper[0]
   - tempcooledtolu[0] = 0
 GC30: compressor_state[1] = 0 -> predictedtemplowerupper[1]
   - tempheatedtolu[1] = 0
 GC31: compressor_state[1] = 1 -> predictedtemplowerupper[1]
   - tempcooledtolu[1] = 0
 GC34: compressor_state[2] = 0 -> predictedtemplowerupper[2]
   - tempheatedtolu[2] = 0
 GC35: compressor_state[2] = 1 -> predictedtemplowerupper[2]
   - tempcooledtolu[2] = 0
 GC38: compressor_state[3] = 0 -> predictedtemplowerupper[3]
   - tempheatedtolu[3] = 0
 GC39: compressor_state[3] = 1 -> predictedtemplowerupper[3]
   - tempcooledtolu[3] = 0
 GC42: compressor_state[4] = 0 -> predictedtemplowerupper[4]
   - tempheatedtolu[4] = 0
 GC43: compressor_state[4] = 1 -> predictedtemplowerupper[4]
   - tempcooledtolu[4] = 0
 GC46: compressor_state[5] = 0 -> predictedtemplowerupper[5]
   - tempheatedtolu[5] = 0
 GC47: compressor_state[5] = 1 -> predictedtemplowerupper[5]
   - tempcooledtolu[5] = 0
Bounds
Binaries
 compressor_state[0] compressor_state[1] compressor_state[2]
 compressor_state[3] compressor_state[4] compressor_state[5]
General Constraints
 GC0: htimemed^2[0] = POW ( htimemed[0] ^ 2 )
 GC1: ctimemed^2[0] = POW ( ctimemed[0] ^ 2 )
 GC4: htimemed^2[1] = POW ( htimemed[1] ^ 2 )
 GC5: ctimemed^2[1] = POW ( ctimemed[1] ^ 2 )
 GC8: htimemed^2[2] = POW ( htimemed[2] ^ 2 )
 GC9: ctimemed^2[2] = POW ( ctimemed[2] ^ 2 )
 GC12: htimemed^2[3] = POW ( htimemed[3] ^ 2 )
 GC13: ctimemed^2[3] = POW ( ctimemed[3] ^ 2 )
 GC16: htimemed^2[4] = POW ( htimemed[4] ^ 2 )
 GC17: ctimemed^2[4] = POW ( ctimemed[4] ^ 2 )
 GC20: htimemed^2[5] = POW ( htimemed[5] ^ 2 )
 GC21: ctimemed^2[5] = POW ( ctimemed[5] ^ 2 )
 GC24: htimefull^2[0] = POW ( htimefull[0] ^ 2 )
 GC25: ctimefull^2[0] = POW ( ctimefull[0] ^ 2 )
 GC28: htimefull^2[1] = POW ( htimefull[1] ^ 2 )
 GC29: ctimefull^2[1] = POW ( ctimefull[1] ^ 2 )
 GC32: htimefull^2[2] = POW ( htimefull[2] ^ 2 )
 GC33: ctimefull^2[2] = POW ( ctimefull[2] ^ 2 )
 GC36: htimefull^2[3] = POW ( htimefull[3] ^ 2 )
 GC37: ctimefull^2[3] = POW ( ctimefull[3] ^ 2 )
 GC40: htimefull^2[4] = POW ( htimefull[4] ^ 2 )
 GC41: ctimefull^2[4] = POW ( ctimefull[4] ^ 2 )
 GC44: htimefull^2[5] = POW ( htimefull[5] ^ 2 )
 GC45: ctimefull^2[5] = POW ( ctimefull[5] ^ 2 )
End
