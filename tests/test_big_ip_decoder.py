from ptscripts.exploitation.big_ip_decoder import run_big_ip_decoder


def test_run_big_ip_decoder():
    encoded_string = '110536896.20480.0000'
    second_encoded_string = '1677687402.36895.0000'
    expected = ('192.168.150.6', '80')
    second_expected = ('106.122.255.99', '8080')
    assert expected == run_big_ip_decoder(encoded_string)
    assert second_expected == run_big_ip_decoder(second_encoded_string)
