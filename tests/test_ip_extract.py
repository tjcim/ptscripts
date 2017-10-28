from ptscripts import ip_extract


def test_cidr_to_ip_list():
    cidr = '192.168.1.0/29'
    expected = ['192.168.1.1', '192.168.1.2', '192.168.1.3', '192.168.1.4', '192.168.1.5',
                '192.168.1.6']
    assert ip_extract.cidr_to_ip_list(cidr) == expected


def test_dashed_last_octect_to_list():
    """ This tests whether the function can return the appropriate values when provided
    an ip such as 192.168.1.1-5 note that the first 3 octets are only present in the first
    part of the string."""
    dashed = '192.168.2.20-30'
    expected = ['192.168.2.20', '192.168.2.21', '192.168.2.22', '192.168.2.23', '192.168.2.24',
                '192.168.2.25', '192.168.2.26', '192.168.2.27', '192.168.2.28', '192.168.2.29',
                '192.168.2.30']
    assert ip_extract.dashed_ips_to_list(dashed) == expected


def test_dashed_full_to_list():
    """ This tests whether the extract_ips can return the appropriate values when provided
    an ip such as 192.168.1.1-192.168.1.30 note that this has the first three octets on both
    sides of the dash."""
    dashed = '192.168.2.20-192.168.2.30'
    expected = ['192.168.2.20', '192.168.2.21', '192.168.2.22', '192.168.2.23', '192.168.2.24',
                '192.168.2.25', '192.168.2.26', '192.168.2.27', '192.168.2.28', '192.168.2.29',
                '192.168.2.30']
    assert ip_extract.dashed_ips_to_list(dashed) == expected


def test_dashed_ips_raise_valueerror_when_third_octet_changes():
    dashed = '192.168.1.1-192.168.2.1'
    assert ip_extract.dashed_ips_to_list(dashed) is None


def test_extract_ips(tmpdir):
    tmp_input = tmpdir.join('input.txt')
    tmp_output = tmpdir.join('_ips.txt')

    # Create test file
    with open(tmp_input.strpath, 'w') as f:
        f.write('\r\n'.join([ip for ip in ['10.0.5.0/29', '10.0.5.55-65', '10.0.6.1', '10.0.6.2']]))

    # Call function
    args = ip_extract.parse_args([tmp_input.strpath, tmpdir.strpath])
    ip_extract.extract_ips(args)

    # Extract results to list
    with open(tmp_output.strpath, 'r') as f:
        lines = [line.strip() for line in f]

    # Create expected
    expected = ip_extract.cidr_to_ip_list('10.0.5.0/29') + ip_extract.dashed_ips_to_list('10.0.5.55-65')
    expected.append('10.0.6.1')
    expected.append('10.0.6.2')

    # Compare
    assert lines == expected
