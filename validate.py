import numpy as np

from loader import get_patient_by_EMPI
from model_tester import get_preprocessed_patients
from value_extractor_transformer import EFTransformer, LBBBTransformer, SinusRhythmTransformer, QRSTransformer, NYHATransformer, NICMTransformer

print "Evaluating EF:"
if True:
    X, Y = get_preprocessed_patients(sample_size=906)

    supp = []
    results = []
    for i in range(len(X)):
        p = get_patient_by_EMPI(X[i])
        if p['Supplemental']:
            supp.append(p['NEW_EMPI'])
            calculated_ef = Y[i]
            ef_delta = int(p['Supplemental']['changle LVEF'])
            empi = p['NEW_EMPI']
            result = (empi, calculated_ef, ef_delta)
            results.append(result)
            print result

    print supp
    #print results
else:
    supp = [u'FAKE_EMPI_2', u'FAKE_EMPI_8', u'FAKE_EMPI_10', u'FAKE_EMPI_11', u'FAKE_EMPI_12', u'FAKE_EMPI_14', u'FAKE_EMPI_16', u'FAKE_EMPI_20', u'FAKE_EMPI_28', u'FAKE_EMPI_29', u'FAKE_EMPI_36', u'FAKE_EMPI_37', u'FAKE_EMPI_38', u'FAKE_EMPI_45', u'FAKE_EMPI_46', u'FAKE_EMPI_52', u'FAKE_EMPI_53', u'FAKE_EMPI_55', u'FAKE_EMPI_56', u'FAKE_EMPI_57', u'FAKE_EMPI_63', u'FAKE_EMPI_64', u'FAKE_EMPI_66', u'FAKE_EMPI_67', u'FAKE_EMPI_68', u'FAKE_EMPI_69', u'FAKE_EMPI_80', u'FAKE_EMPI_82', u'FAKE_EMPI_88', u'FAKE_EMPI_90', u'FAKE_EMPI_91', u'FAKE_EMPI_95', u'FAKE_EMPI_98', u'FAKE_EMPI_99', u'FAKE_EMPI_100', u'FAKE_EMPI_101', u'FAKE_EMPI_103', u'FAKE_EMPI_108', u'FAKE_EMPI_109', u'FAKE_EMPI_119', u'FAKE_EMPI_120', u'FAKE_EMPI_122', u'FAKE_EMPI_123', u'FAKE_EMPI_124', u'FAKE_EMPI_126', u'FAKE_EMPI_129', u'FAKE_EMPI_135', u'FAKE_EMPI_141', u'FAKE_EMPI_161', u'FAKE_EMPI_162', u'FAKE_EMPI_165', u'FAKE_EMPI_166', u'FAKE_EMPI_170', u'FAKE_EMPI_175', u'FAKE_EMPI_178', u'FAKE_EMPI_181', u'FAKE_EMPI_185', u'FAKE_EMPI_186', u'FAKE_EMPI_190', u'FAKE_EMPI_191', u'FAKE_EMPI_193', u'FAKE_EMPI_194', u'FAKE_EMPI_196', u'FAKE_EMPI_197', u'FAKE_EMPI_200', u'FAKE_EMPI_201', u'FAKE_EMPI_203', u'FAKE_EMPI_206', u'FAKE_EMPI_209', u'FAKE_EMPI_210', u'FAKE_EMPI_213', u'FAKE_EMPI_215', u'FAKE_EMPI_216', u'FAKE_EMPI_224', u'FAKE_EMPI_225', u'FAKE_EMPI_226', u'FAKE_EMPI_227', u'FAKE_EMPI_228', u'FAKE_EMPI_234', u'FAKE_EMPI_238', u'FAKE_EMPI_240', u'FAKE_EMPI_241', u'FAKE_EMPI_242', u'FAKE_EMPI_254', u'FAKE_EMPI_257', u'FAKE_EMPI_263', u'FAKE_EMPI_269', u'FAKE_EMPI_270', u'FAKE_EMPI_275', u'FAKE_EMPI_281', u'FAKE_EMPI_282', u'FAKE_EMPI_286', u'FAKE_EMPI_287', u'FAKE_EMPI_289', u'FAKE_EMPI_290', u'FAKE_EMPI_292', u'FAKE_EMPI_293', u'FAKE_EMPI_294', u'FAKE_EMPI_297', u'FAKE_EMPI_301', u'FAKE_EMPI_302', u'FAKE_EMPI_305', u'FAKE_EMPI_306', u'FAKE_EMPI_309', u'FAKE_EMPI_310', u'FAKE_EMPI_311', u'FAKE_EMPI_312', u'FAKE_EMPI_313', u'FAKE_EMPI_315', u'FAKE_EMPI_316', u'FAKE_EMPI_317', u'FAKE_EMPI_322', u'FAKE_EMPI_323', u'FAKE_EMPI_326', u'FAKE_EMPI_327', u'FAKE_EMPI_333', u'FAKE_EMPI_342', u'FAKE_EMPI_344', u'FAKE_EMPI_349', u'FAKE_EMPI_355', u'FAKE_EMPI_358', u'FAKE_EMPI_359', u'FAKE_EMPI_360', u'FAKE_EMPI_361', u'FAKE_EMPI_362', u'FAKE_EMPI_365', u'FAKE_EMPI_368', u'FAKE_EMPI_380', u'FAKE_EMPI_382', u'FAKE_EMPI_386', u'FAKE_EMPI_390', u'FAKE_EMPI_391', u'FAKE_EMPI_392', u'FAKE_EMPI_396', u'FAKE_EMPI_397', u'FAKE_EMPI_399', u'FAKE_EMPI_401', u'FAKE_EMPI_402', u'FAKE_EMPI_407', u'FAKE_EMPI_419', u'FAKE_EMPI_425', u'FAKE_EMPI_427', u'FAKE_EMPI_428', u'FAKE_EMPI_430', u'FAKE_EMPI_432', u'FAKE_EMPI_434', u'FAKE_EMPI_436', u'FAKE_EMPI_438', u'FAKE_EMPI_440', u'FAKE_EMPI_441', u'FAKE_EMPI_443', u'FAKE_EMPI_445', u'FAKE_EMPI_446', u'FAKE_EMPI_447', u'FAKE_EMPI_463', u'FAKE_EMPI_465', u'FAKE_EMPI_480', u'FAKE_EMPI_481', u'FAKE_EMPI_484', u'FAKE_EMPI_488', u'FAKE_EMPI_491', u'FAKE_EMPI_496', u'FAKE_EMPI_497', u'FAKE_EMPI_500', u'FAKE_EMPI_501', u'FAKE_EMPI_508', u'FAKE_EMPI_510', u'FAKE_EMPI_513', u'FAKE_EMPI_514', u'FAKE_EMPI_515', u'FAKE_EMPI_526', u'FAKE_EMPI_528', u'FAKE_EMPI_531', u'FAKE_EMPI_534', u'FAKE_EMPI_536', u'FAKE_EMPI_539', u'FAKE_EMPI_541', u'FAKE_EMPI_547', u'FAKE_EMPI_549', u'FAKE_EMPI_559', u'FAKE_EMPI_563', u'FAKE_EMPI_568', u'FAKE_EMPI_569', u'FAKE_EMPI_570', u'FAKE_EMPI_582', u'FAKE_EMPI_583', u'FAKE_EMPI_587', u'FAKE_EMPI_590', u'FAKE_EMPI_591', u'FAKE_EMPI_607', u'FAKE_EMPI_613', u'FAKE_EMPI_614', u'FAKE_EMPI_616', u'FAKE_EMPI_619', u'FAKE_EMPI_622', u'FAKE_EMPI_623', u'FAKE_EMPI_627', u'FAKE_EMPI_631', u'FAKE_EMPI_633', u'FAKE_EMPI_634', u'FAKE_EMPI_635', u'FAKE_EMPI_638', u'FAKE_EMPI_639', u'FAKE_EMPI_642', u'FAKE_EMPI_644', u'FAKE_EMPI_650', u'FAKE_EMPI_651', u'FAKE_EMPI_656', u'FAKE_EMPI_658', u'FAKE_EMPI_660', u'FAKE_EMPI_662', u'FAKE_EMPI_663', u'FAKE_EMPI_668', u'FAKE_EMPI_670', u'FAKE_EMPI_673', u'FAKE_EMPI_675', u'FAKE_EMPI_677', u'FAKE_EMPI_678', u'FAKE_EMPI_679', u'FAKE_EMPI_682', u'FAKE_EMPI_691', u'FAKE_EMPI_694', u'FAKE_EMPI_696', u'FAKE_EMPI_705', u'FAKE_EMPI_706', u'FAKE_EMPI_708', u'FAKE_EMPI_710', u'FAKE_EMPI_713', u'FAKE_EMPI_715', u'FAKE_EMPI_716', u'FAKE_EMPI_723', u'FAKE_EMPI_729', u'FAKE_EMPI_730', u'FAKE_EMPI_731', u'FAKE_EMPI_733', u'FAKE_EMPI_735', u'FAKE_EMPI_738', u'FAKE_EMPI_739', u'FAKE_EMPI_741', u'FAKE_EMPI_744', u'FAKE_EMPI_748', u'FAKE_EMPI_751', u'FAKE_EMPI_753', u'FAKE_EMPI_757', u'FAKE_EMPI_762', u'FAKE_EMPI_768', u'FAKE_EMPI_769', u'FAKE_EMPI_774', u'FAKE_EMPI_777', u'FAKE_EMPI_780', u'FAKE_EMPI_781', u'FAKE_EMPI_785', u'FAKE_EMPI_790', u'FAKE_EMPI_792', u'FAKE_EMPI_800', u'FAKE_EMPI_803', u'FAKE_EMPI_807', u'FAKE_EMPI_820', u'FAKE_EMPI_824', u'FAKE_EMPI_826', u'FAKE_EMPI_827', u'FAKE_EMPI_829', u'FAKE_EMPI_830', u'FAKE_EMPI_832', u'FAKE_EMPI_838', u'FAKE_EMPI_839', u'FAKE_EMPI_840', u'FAKE_EMPI_843', u'FAKE_EMPI_851', u'FAKE_EMPI_853', u'FAKE_EMPI_858', u'FAKE_EMPI_859', u'FAKE_EMPI_863', u'FAKE_EMPI_866', u'FAKE_EMPI_873', u'FAKE_EMPI_876', u'FAKE_EMPI_878', u'FAKE_EMPI_881', u'FAKE_EMPI_884', u'FAKE_EMPI_885', u'FAKE_EMPI_886', u'FAKE_EMPI_891', u'FAKE_EMPI_895', u'FAKE_EMPI_900', u'FAKE_EMPI_903', u'FAKE_EMPI_904']
    results = [(u'FAKE_EMPI_2', 0.0, 11), (u'FAKE_EMPI_8', 10.0, 10), (u'FAKE_EMPI_10', 14.0, 11), (u'FAKE_EMPI_11', 13.0, 8), (u'FAKE_EMPI_12', 26.0, 1), (u'FAKE_EMPI_14', 32.0, 21), (u'FAKE_EMPI_16', 14.0, -1), (u'FAKE_EMPI_20', 15.0, 23), (u'FAKE_EMPI_28', 37.0, 0), (u'FAKE_EMPI_29', 0.0, -3), (u'FAKE_EMPI_36', 22.0, 30), (u'FAKE_EMPI_37', -2.0, -2), (u'FAKE_EMPI_38', -24.0, 3), (u'FAKE_EMPI_45', 11.0, 21), (u'FAKE_EMPI_46', 0.0, 16), (u'FAKE_EMPI_52', 24.0, 18), (u'FAKE_EMPI_53', 14.0, -7), (u'FAKE_EMPI_55', 1.0, 4), (u'FAKE_EMPI_56', 18.0, 4), (u'FAKE_EMPI_57', 12.0, -2), (u'FAKE_EMPI_63', 26.0, 26), (u'FAKE_EMPI_64', 11.0, 10), (u'FAKE_EMPI_66', 4.0, 4), (u'FAKE_EMPI_67', 16.0, 16), (u'FAKE_EMPI_68', 20.0, 23), (u'FAKE_EMPI_69', 1.0, -5), (u'FAKE_EMPI_80', -3.0, 11), (u'FAKE_EMPI_82', 6.0, -4), (u'FAKE_EMPI_88', 15.0, 15), (u'FAKE_EMPI_90', 7.0, 7), (u'FAKE_EMPI_91', 21.0, 20), (u'FAKE_EMPI_95', 24.0, 24), (u'FAKE_EMPI_98', 4.0, 8), (u'FAKE_EMPI_99', 0.0, -5), (u'FAKE_EMPI_100', 18.0, 27), (u'FAKE_EMPI_101', 15.0, 8), (u'FAKE_EMPI_103', 2.0, 2), (u'FAKE_EMPI_108', 1.0, 1), (u'FAKE_EMPI_109', -2.0, -2), (u'FAKE_EMPI_119', -24.0, 6), (u'FAKE_EMPI_120', 15.0, 19), (u'FAKE_EMPI_122', 0.0, -2), (u'FAKE_EMPI_123', 37.0, 29), (u'FAKE_EMPI_124', 4.0, 6), (u'FAKE_EMPI_126', 7.0, 14), (u'FAKE_EMPI_129', 0.0, -4), (u'FAKE_EMPI_135', -28.0, -9), (u'FAKE_EMPI_141', 35.0, 31), (u'FAKE_EMPI_161', 10.0, 5), (u'FAKE_EMPI_162', 28.0, 16), (u'FAKE_EMPI_165', 11.0, 5), (u'FAKE_EMPI_166', -23.0, 5), (u'FAKE_EMPI_170', 11.0, 24), (u'FAKE_EMPI_175', 26.0, 13), (u'FAKE_EMPI_178', 15.0, 11), (u'FAKE_EMPI_181', -1.0, 12), (u'FAKE_EMPI_185', 0.0, -1), (u'FAKE_EMPI_186', 2.0, 4), (u'FAKE_EMPI_190', 47.0, 39), (u'FAKE_EMPI_191', 15.0, 15), (u'FAKE_EMPI_193', 2.0, 2), (u'FAKE_EMPI_194', -4.0, 4), (u'FAKE_EMPI_196', -2.0, -4), (u'FAKE_EMPI_197', -3.0, -1), (u'FAKE_EMPI_200', 5.0, 8), (u'FAKE_EMPI_201', 3.0, 4), (u'FAKE_EMPI_203', 1.0, 1), (u'FAKE_EMPI_206', 5.0, 12), (u'FAKE_EMPI_209', 1.0, 4), (u'FAKE_EMPI_210', 17.0, 17), (u'FAKE_EMPI_213', 7.0, 6), (u'FAKE_EMPI_215', -5.0, -8), (u'FAKE_EMPI_216', 65.0, 6), (u'FAKE_EMPI_224', 20.0, 9), (u'FAKE_EMPI_225', 8.0, 12), (u'FAKE_EMPI_226', 4.0, 9), (u'FAKE_EMPI_227', -10.0, 16), (u'FAKE_EMPI_228', 12.0, 12), (u'FAKE_EMPI_234', 15.0, 9), (u'FAKE_EMPI_238', 13.0, 13), (u'FAKE_EMPI_240', 22.0, 7), (u'FAKE_EMPI_241', -18.0, 6), (u'FAKE_EMPI_242', -1.0, 3), (u'FAKE_EMPI_254', 9.0, 9), (u'FAKE_EMPI_257', 5.0, -1), (u'FAKE_EMPI_263', 4.0, 3), (u'FAKE_EMPI_269', -1.0, -1), (u'FAKE_EMPI_270', 6.0, 20), (u'FAKE_EMPI_275', 18.0, 0), (u'FAKE_EMPI_281', -3.0, -2), (u'FAKE_EMPI_282', -8.0, -6), (u'FAKE_EMPI_286', 13.0, 13), (u'FAKE_EMPI_287', 25.0, 10), (u'FAKE_EMPI_289', 22.0, 21), (u'FAKE_EMPI_290', -7.0, 8), (u'FAKE_EMPI_292', 5.0, 7), (u'FAKE_EMPI_293', 9.0, 10), (u'FAKE_EMPI_294', 6.0, 17), (u'FAKE_EMPI_297', 15.0, 24), (u'FAKE_EMPI_301', -3.0, -3), (u'FAKE_EMPI_302', 24.0, 19), (u'FAKE_EMPI_305', 3.0, 1), (u'FAKE_EMPI_306', 16.0, 11), (u'FAKE_EMPI_309', 14.0, 14), (u'FAKE_EMPI_310', 16.0, 11), (u'FAKE_EMPI_311', 3.0, -5), (u'FAKE_EMPI_312', 41.0, 3), (u'FAKE_EMPI_313', 22.0, 2), (u'FAKE_EMPI_315', 16.0, 6), (u'FAKE_EMPI_316', 21.0, 22), (u'FAKE_EMPI_317', -16.0, -6), (u'FAKE_EMPI_322', -14.0, 0), (u'FAKE_EMPI_323', 9.0, 8), (u'FAKE_EMPI_326', 11.0, 11), (u'FAKE_EMPI_327', 17.0, 17), (u'FAKE_EMPI_333', -20.0, -10), (u'FAKE_EMPI_342', 28.0, 25), (u'FAKE_EMPI_344', -5.0, -1), (u'FAKE_EMPI_349', 63.0, -4), (u'FAKE_EMPI_355', 1.0, 5), (u'FAKE_EMPI_358', -19.0, -9), (u'FAKE_EMPI_359', 27.0, 9), (u'FAKE_EMPI_360', -11.0, -11), (u'FAKE_EMPI_361', -14.0, 0), (u'FAKE_EMPI_362', 27.0, 25), (u'FAKE_EMPI_365', 15.0, 20), (u'FAKE_EMPI_368', -9.0, -9), (u'FAKE_EMPI_380', -8.0, 4), (u'FAKE_EMPI_382', -1.0, 1), (u'FAKE_EMPI_386', 4.0, -1), (u'FAKE_EMPI_390', 8.0, 8), (u'FAKE_EMPI_391', 5.0, -2), (u'FAKE_EMPI_392', 36.0, 29), (u'FAKE_EMPI_396', 24.0, 24), (u'FAKE_EMPI_397', 62.0, -1), (u'FAKE_EMPI_399', -4.0, 8), (u'FAKE_EMPI_401', 44.0, 29), (u'FAKE_EMPI_402', 0.0, 15), (u'FAKE_EMPI_407', -3.0, -4), (u'FAKE_EMPI_419', 24.0, 14), (u'FAKE_EMPI_425', -3.0, -3), (u'FAKE_EMPI_427', 1.0, 1), (u'FAKE_EMPI_428', 27.0, 16), (u'FAKE_EMPI_430', 1.0, 2), (u'FAKE_EMPI_432', 27.0, 24), (u'FAKE_EMPI_434', 4.0, 2), (u'FAKE_EMPI_436', 17.0, 8), (u'FAKE_EMPI_438', 21.0, 13), (u'FAKE_EMPI_440', 3.0, 8), (u'FAKE_EMPI_441', 15.0, 14), (u'FAKE_EMPI_443', 4.0, 4), (u'FAKE_EMPI_445', 10.0, 10), (u'FAKE_EMPI_446', 19.0, 19), (u'FAKE_EMPI_447', 3.0, 3), (u'FAKE_EMPI_463', 6.0, 6), (u'FAKE_EMPI_465', 10.0, 10), (u'FAKE_EMPI_480', 4.0, 6), (u'FAKE_EMPI_481', 24.0, 12), (u'FAKE_EMPI_484', -3.0, -4), (u'FAKE_EMPI_488', 22.0, 13), (u'FAKE_EMPI_491', -4.0, -4), (u'FAKE_EMPI_496', 24.0, 10), (u'FAKE_EMPI_497', -1.0, -1), (u'FAKE_EMPI_500', 12.0, 12), (u'FAKE_EMPI_501', 17.0, 12), (u'FAKE_EMPI_508', 0.0, -3), (u'FAKE_EMPI_510', 20.0, 3), (u'FAKE_EMPI_513', 16.0, 6), (u'FAKE_EMPI_514', 18.0, 8), (u'FAKE_EMPI_515', 4.0, 4), (u'FAKE_EMPI_526', 38.0, 26), (u'FAKE_EMPI_528', 28.0, 17), (u'FAKE_EMPI_531', 5.0, 0), (u'FAKE_EMPI_534', 25.0, 3), (u'FAKE_EMPI_536', -6.0, -6), (u'FAKE_EMPI_539', 15.0, 0), (u'FAKE_EMPI_541', 1.0, 4), (u'FAKE_EMPI_547', 14.0, 7), (u'FAKE_EMPI_549', 7.0, 3), (u'FAKE_EMPI_559', -5.0, -3), (u'FAKE_EMPI_563', 19.0, 9), (u'FAKE_EMPI_568', 14.0, 14), (u'FAKE_EMPI_569', 17.0, 17), (u'FAKE_EMPI_570', 26.0, 16), (u'FAKE_EMPI_582', -20.0, -9), (u'FAKE_EMPI_583', 2.0, 2), (u'FAKE_EMPI_587', 2.0, -1), (u'FAKE_EMPI_590', 5.0, 4), (u'FAKE_EMPI_591', 7.0, -7), (u'FAKE_EMPI_607', 3.0, -1), (u'FAKE_EMPI_613', 18.0, 4), (u'FAKE_EMPI_614', 23.0, 7), (u'FAKE_EMPI_616', 18.0, 12), (u'FAKE_EMPI_619', -2.0, -3), (u'FAKE_EMPI_622', 11.0, 10), (u'FAKE_EMPI_623', 0.0, 15), (u'FAKE_EMPI_627', 22.0, 1), (u'FAKE_EMPI_631', 5.0, 5), (u'FAKE_EMPI_633', 1.0, 0), (u'FAKE_EMPI_634', -2.0, -2), (u'FAKE_EMPI_635', -4.0, -4), (u'FAKE_EMPI_638', -1.0, 0), (u'FAKE_EMPI_639', -25.0, 23), (u'FAKE_EMPI_642', 9.0, 9), (u'FAKE_EMPI_644', 22.0, 12), (u'FAKE_EMPI_650', 41.0, -9), (u'FAKE_EMPI_651', 20.0, 14), (u'FAKE_EMPI_656', 6.0, 6), (u'FAKE_EMPI_658', 11.0, 12), (u'FAKE_EMPI_660', -21.0, -5), (u'FAKE_EMPI_662', 20.0, 10), (u'FAKE_EMPI_663', 4.0, 0), (u'FAKE_EMPI_668', 20.0, 13), (u'FAKE_EMPI_670', -5.0, -5), (u'FAKE_EMPI_673', 22.0, 30), (u'FAKE_EMPI_675', 31.0, 2), (u'FAKE_EMPI_677', 2.0, 2), (u'FAKE_EMPI_678', 23.0, 23), (u'FAKE_EMPI_679', 63.0, -6), (u'FAKE_EMPI_682', 1.0, -3), (u'FAKE_EMPI_691', 12.0, 6), (u'FAKE_EMPI_694', 4.0, 5), (u'FAKE_EMPI_696', 11.0, 19), (u'FAKE_EMPI_705', -2.0, -2), (u'FAKE_EMPI_706', 5.0, 5), (u'FAKE_EMPI_708', 5.0, -3), (u'FAKE_EMPI_710', 8.0, 1), (u'FAKE_EMPI_713', 22.0, 10), (u'FAKE_EMPI_715', 16.0, 21), (u'FAKE_EMPI_716', -16.0, -2), (u'FAKE_EMPI_723', 20.0, 3), (u'FAKE_EMPI_729', 7.0, 25), (u'FAKE_EMPI_730', 8.0, 10), (u'FAKE_EMPI_731', -14.0, -4), (u'FAKE_EMPI_733', 15.0, 0), (u'FAKE_EMPI_735', 25.0, 15), (u'FAKE_EMPI_738', 2.0, -1), (u'FAKE_EMPI_739', -1.0, 14), (u'FAKE_EMPI_741', 0.0, 1), (u'FAKE_EMPI_744', 1.0, 1), (u'FAKE_EMPI_748', -10.0, -10), (u'FAKE_EMPI_751', 7.0, 7), (u'FAKE_EMPI_753', -2.0, -1), (u'FAKE_EMPI_757', 7.0, -6), (u'FAKE_EMPI_762', 33.0, 21), (u'FAKE_EMPI_768', 0.0, 0), (u'FAKE_EMPI_769', 13.0, 7), (u'FAKE_EMPI_774', -15.0, 12), (u'FAKE_EMPI_777', 20.0, 17), (u'FAKE_EMPI_780', -3.0, -3), (u'FAKE_EMPI_781', 9.0, 9), (u'FAKE_EMPI_785', 19.0, 9), (u'FAKE_EMPI_790', 36.0, 36), (u'FAKE_EMPI_792', 11.0, -4), (u'FAKE_EMPI_800', 29.0, 21), (u'FAKE_EMPI_803', 3.0, 2), (u'FAKE_EMPI_807', 4.0, 4), (u'FAKE_EMPI_820', -1.0, 4), (u'FAKE_EMPI_824', 28.0, 9), (u'FAKE_EMPI_826', 16.0, 10), (u'FAKE_EMPI_827', 2.0, 2), (u'FAKE_EMPI_829', 17.0, -10), (u'FAKE_EMPI_830', -19.0, 6), (u'FAKE_EMPI_832', 13.0, 12), (u'FAKE_EMPI_838', 8.0, 7), (u'FAKE_EMPI_839', 18.0, -1), (u'FAKE_EMPI_840', 4.0, 2), (u'FAKE_EMPI_843', 6.0, 2), (u'FAKE_EMPI_851', 16.0, -2), (u'FAKE_EMPI_853', -3.0, -3), (u'FAKE_EMPI_858', -20.0, -5), (u'FAKE_EMPI_859', 27.0, 27), (u'FAKE_EMPI_863', 24.0, -2), (u'FAKE_EMPI_866', -9.0, -13), (u'FAKE_EMPI_873', 24.0, 23), (u'FAKE_EMPI_876', 3.0, 13), (u'FAKE_EMPI_878', 9.0, 9), (u'FAKE_EMPI_881', 9.0, 9), (u'FAKE_EMPI_884', 13.0, 3), (u'FAKE_EMPI_885', 16.0, 9), (u'FAKE_EMPI_886', 2.0, 1), (u'FAKE_EMPI_891', -3.0, 3), (u'FAKE_EMPI_895', 8.0, 16), (u'FAKE_EMPI_900', 12.0, -3), (u'FAKE_EMPI_903', 1.0, -7), (u'FAKE_EMPI_904', -8.0, -12)]


def report_standard_metrics(X,Y):
    tp = 0
    tn = 0
    fp = 0
    fn = 0
    wrong = []
    for i in range(len(X)):
        pred = X[i]
        actual = Y[i]
        if pred and actual:
            tp += 1
        elif not pred and not actual:
            tn += 1
        elif pred and not actual:
            wrong.append(i)
            fp += 1
        elif not pred and actual:
            wrong.append(i)
            fn += 1

    print "Sensitivity:"
    print float(tp)/(tp + fn)

    print "Specificity:"
    print float(tn)/(tn + fp)

    print "Accuracy:"
    print float(tp + tn)/(tp + tn + fp + fn)

    return wrong


distance = []
cutoff = 5
preds = []
actuals = []
for result in results:
    (empi, pred, actual) = result
    distance.append(abs(pred - actual))
    preds.append(pred < cutoff)
    actuals.append(actual < cutoff)

        
print "Avg Distance:"
print np.average(distance)

wrong = report_standard_metrics(preds, actuals)

print "Wrong:"
print np.array(supp)[wrong]



print "Evaluating LBBB:"
t = LBBBTransformer(time_horizon=30*3)

patients = []
actuals = []
for key in supp:
    p = get_patient_by_EMPI(key)
    try:
        actuals.append(int(p['Supplemental']['LBBB']))
        patients.append(p)
    except:
        pass
preds = t.transform(patients)

wrong = report_standard_metrics(preds, actuals)
print "Wrong:"
print np.array(patients)[wrong]
