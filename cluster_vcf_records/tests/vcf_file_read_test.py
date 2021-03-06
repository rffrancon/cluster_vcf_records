import os
import unittest

from cluster_vcf_records import vcf_file_read, vcf_record

modules_dir = os.path.dirname(os.path.abspath(vcf_file_read.__file__))
data_dir = os.path.join(modules_dir, 'tests', 'data', 'vcf_file_read')



class TestVcfFileRead(unittest.TestCase):
    def test_vcf_file_to_dict(self):
        '''test vcf_file_to_dict'''
        expected_header = ['# header1', '# header2']
        lines = [
            'ref_42\t11\tid_foo\tA\tG\t42.42\tPASS\tKMER=31;SVLEN=0;SVTYPE=SNP\tGT:COV:GT_CONF\t1/1:0,52:39.80',
            'ref_42\t12\tid_foo\tC\tG\t42.43\tPASS\tKMER=31;SVLEN=0;SVTYPE=SNP\tGT:COV:GT_CONF\t1/1:0,53:39.81',
            'ref_43\t42\tid_foo\tT\tG\t43.42\tPASS\tKMER=31;SVLEN=0;SVTYPE=SNP\tGT:COV:GT_CONF\t1/1:0,54:39.82',
            'ref_43\t43\tid_foo\tT\tG,*\t43.42\tPASS\tKMER=31;SVLEN=0;SVTYPE=SNP\tGT:COV:GT_CONF\t1/1:0,54:39.83',
            'ref_43\t44\tid_foo\tT\t*\t43.42\tPASS\tKMER=31;SVLEN=0;SVTYPE=SNP\tGT:COV:GT_CONF\t1/1:0,54:39.84',
        ]

        expected_records = {
            'ref_42': [vcf_record.VcfRecord(lines[0]), vcf_record.VcfRecord(lines[1])],
            'ref_43': [vcf_record.VcfRecord(lines[x]) for x in (2, 3, 4)],
        }

        infile = os.path.join(data_dir, 'vcf_file_to_dict.vcf')
        got_header, got_records = vcf_file_read.vcf_file_to_dict(infile)
        self.assertEqual(expected_records, got_records)
        self.assertEqual(expected_header, got_header)

        infile = os.path.join(data_dir, 'vcf_file_to_dict.vcf.gz')
        got_header, got_records = vcf_file_read.vcf_file_to_dict(infile)
        self.assertEqual(expected_records, got_records)
        self.assertEqual(expected_header, got_header)


        expected_records['ref_43'].pop()
        expected_records['ref_43'][-1].remove_asterisk_alts()
        infile = os.path.join(data_dir, 'vcf_file_to_dict.vcf')
        got_header, got_records = vcf_file_read.vcf_file_to_dict(infile, remove_asterisk_alts=True)
        self.assertEqual(expected_records, got_records)
        self.assertEqual(expected_header, got_header)


    def test_vcf_file_to_list(self):
        '''test vcf_file_to_list'''
        expected_header = ['# header1', '# header2']
        lines = [
            'ref_42\t12\tid_foo\tC\tG\t42.43\tPASS\tKMER=31;SVLEN=0;SVTYPE=SNP\tGT:COV:GT_CONF\t1/1:0,53:39.81',
            'ref_42\t11\tid_foo\tA\tG\t42.42\tPASS\tKMER=31;SVLEN=0;SVTYPE=SNP\tGT:COV:GT_CONF\t1/1:0,52:39.80',
            'ref_43\t42\tid_foo\tT\tG\t43.42\tPASS\tKMER=31;SVLEN=0;SVTYPE=SNP\tGT:COV:GT_CONF\t1/1:0,54:39.82',
        ]
        expected_records = [vcf_record.VcfRecord(x) for x in lines]
        infile = os.path.join(data_dir, 'vcf_file_to_list.vcf')
        got_header, got_records = vcf_file_read.vcf_file_to_list(infile)
        self.assertEqual(expected_header, got_header)
        self.assertEqual(expected_records, got_records)

        infile = os.path.join(data_dir, 'vcf_file_to_list.vcf.gz')
        got_header, got_records = vcf_file_read.vcf_file_to_list(infile)
        self.assertEqual(expected_header, got_header)
        self.assertEqual(expected_records, got_records)


    def test_get_sample_name_from_vcf_header_lines(self):
        '''test get_sample_name_from_vcf_header_lines'''
        lines = ['foo', 'bar']
        self.assertEqual(None, vcf_file_read.get_sample_name_from_vcf_header_lines(lines))

        lines.append('#CHROM\twrong!')
        with self.assertRaises(vcf_file_read.Error):
            vcf_file_read.get_sample_name_from_vcf_header_lines(lines)

        lines[-1] = '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO'
        self.assertEqual(None, vcf_file_read.get_sample_name_from_vcf_header_lines(lines))

        lines[-1] = '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT'
        self.assertEqual(None, vcf_file_read.get_sample_name_from_vcf_header_lines(lines))

        lines[-1] = '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tsample_name'
        self.assertEqual('sample_name', vcf_file_read.get_sample_name_from_vcf_header_lines(lines))

        lines[-1] = '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tsample_name\tsample_name_2'
        self.assertEqual('sample_name', vcf_file_read.get_sample_name_from_vcf_header_lines(lines))


    def test_vcf_file_has_at_least_one_record(self):
        '''test vcf_file_has_at_least_one_record'''
        self.assertTrue(vcf_file_read.vcf_file_has_at_least_one_record(os.path.join(data_dir, 'vcf_file_has_at_least_one_record.yes.vcf')))
        self.assertFalse(vcf_file_read.vcf_file_has_at_least_one_record(os.path.join(data_dir, 'vcf_file_has_at_least_one_record.no.vcf')))


    def test_get_header_lines_from_vcf_file(self):
        '''test get_header_lines_from_vcf_file'''
        vcf_with_header = os.path.join(data_dir, 'get_header_lines_from_vcf_file.with_header.vcf')
        vcf_no_header = os.path.join(data_dir, 'get_header_lines_from_vcf_file.no_header.vcf')
        got = vcf_file_read.get_header_lines_from_vcf_file(vcf_with_header)
        expected = ['# header1', '# header2']
        self.assertEqual(expected, got)
        got = vcf_file_read.get_header_lines_from_vcf_file(vcf_no_header)
        self.assertEqual([], got)


    def test_get_sample_name_from_vcf_file(self):
        '''test get_sample_name_from_vcf_file'''
        vcf_no_chrom_line = os.path.join(data_dir, 'get_sample_name_from_vcf_file.no_chrom_line.vcf')
        vcf_sample_42 = os.path.join(data_dir, 'get_sample_name_from_vcf_file.sample_42.vcf')
        vcf_sample_42_43 = os.path.join(data_dir, 'get_sample_name_from_vcf_file.sample_42_and_43.vcf')
        got = vcf_file_read.get_sample_name_from_vcf_file(vcf_no_chrom_line)
        self.assertEqual(None, got)
        got = vcf_file_read.get_sample_name_from_vcf_file(vcf_sample_42)
        self.assertEqual('sample_42', got)
        got = vcf_file_read.get_sample_name_from_vcf_file(vcf_sample_42_43)
        self.assertEqual('sample_42', got)


