#!/usr/local/bin/perl

#��������������������������������������������������������������������
#�� MONKEY BANANA : monkey.cgi - 2014/11/08
#�� copyright (c) KentWeb, 1997-2014
#�� http://www.kent-web.com/
#��������������������������������������������������������������������

# ���W���[���錾
use strict;
use CGI::Carp qw(fatalsToBrowser);

# �ݒ�t�@�C���F��
require "./init.cgi";
my %cf = set_init();

# �f�[�^��
my %in = parse_form();

# ��������
if ($in{mode} eq 'bana') { bana_data(); }
if ($in{mode} eq 'note') { note_page(); }
if ($in{mode} eq 'kuji') { kuji_page(); }
menu_list();

#-----------------------------------------------------------
#  ���j���[���
#-----------------------------------------------------------
sub menu_list {
	# �J�E���^
	my $counter = count_log() if ($cf{counter});

	# �g�b�v�L���ǂݍ���
	open(IN,"$cf{logfile}") or error("open err: $cf{logfile}");
	my $top = <IN>;
	close(IN);

	# �g�b�v�L������
	my ($num,$word) = (split(/<>/,$top))[0,2];
	$num  ||= 1;
	$word ||= "�I�T��";

	# �e���v���[�g�ǂݍ���
	open(IN,"$cf{tmpldir}/monkey.html") or error("open err: monkey.html");
	my $tmpl = join('', <IN>);
	close(IN);

	$tmpl =~ s/!([a-z]+_cgi)!/$cf{$1}/g;
	$tmpl =~ s/!homepage!/$cf{homepage}/g;
	$tmpl =~ s/!num!/$num/g;
	$tmpl =~ s/!word!/$word/g;
	$tmpl =~ s/!cgi_title!/$cf{cgi_title}/g;
	$tmpl =~ s/!counter!/$counter/g;
	$tmpl =~ s|!icon:(\w+\.\w+)!|<img src="$cf{iconurl}/$1" alt="" />|g;

	# �w�b�_�\��
	print "Content-type: text/html; charset=shift_jis\n\n";
	footer($tmpl);
}

#-----------------------------------------------------------
#  �L����t
#-----------------------------------------------------------
sub bana_data {
	# �z�X�g���擾
	my $host = host_chk();

	# ���[�h�`�F�b�N
	word_chk($in{word});

	open(DAT,"+< $cf{logfile}") or error("open err: $cf{logfile}");
	eval "flock(DAT, 2);";
	my $top = <DAT>;

	my ($no,$date,$word,$agent,$hos,$tim);
	if ($top eq "") {
		$top = "1<>$date<>�I�T��<>local<>local<><>\n";
		$no = 1;
	} else {
		($no,$date,$word,$agent,$hos,$tim) = split(/<>/,$top);
	}

	# ����z�X�g����̓��e�͈��Ԋu�̕b��������
	my $time = time;
	if ($host eq $hos && $time - $tim < $cf{term}) {
		close(DAT);
		error("�A���o�^��$cf{term}�b�ȏ�҂��Ă�");
	}

	# �P�O�̌��t���`�F�b�N
	if ($in{no} != $no) {
		close(DAT);
		error("�c�O�A�N������ɘA�z���Ă��܂����悤�ł��B<br />�O��ʂɖ߂��čēǂݍ��݂��ĉ�����");
	}

	my ($i,$flg);
	my @log = ($top);
	while (<DAT>) {
		$i++;
		my ($word) = (split(/<>/))[2];
		if ($in{word} eq $word) { $flg++; last; }

		last if ($i >= $cf{maxlog} - 1);
		push(@log,$_);
	}

	if ($flg) {
		close(DAT);
		error("�c�O�A�N�����������t��A�z�����悤�ł��B<br />�O��ʂɖ߂��đ��̌��t��A�z�������Ă݂Ă�������");
	}

	# �L��NO���̔ԁE���Ԃ��擾
	$no++;
	my $date = get_time();

	# �u���E�U���
	my $hua = $ENV{HTTP_USER_AGENT};
	$hua =~ s/&/&amp;/g;
	$hua =~ s/</&lt;/g;
	$hua =~ s/>/&gt;/g;
	$hua =~ s/"/&quot;/g;

	# ���O���X�V
	unshift(@log,"$no<>$date<>$in{word}<>$hua<>$host<>$time<>\n");
	seek(DAT, 0, 0);
	print DAT @log;
	truncate(DAT, tell(DAT));
	close(DAT);

	# �e���v���[�g�ǂݍ���
	open(IN,"$cf{tmpldir}/word.html") or error("open err: word.html");
	my $tmpl = join('', <IN>);
	close(IN);

	# �����u������
	$tmpl =~ s|!icon:(\w+\.\w+)!|<img src="$cf{iconurl}/$1" alt="" />|g;
	$tmpl =~ s/!cgi_title!/$cf{cgi_title}/g;
	$tmpl =~ s/!monkey_cgi!/$cf{monkey_cgi}/g;

	# �e���v���[�g����
	my ($head,$loop,$foot) = $tmpl =~ /(.+)<!-- loop_begin -->(.+)<!-- loop_end -->(.+)/s
			? ($1,$2,$3)
			: error("�e���v���[�g�s��");

	# ��ʕ\��
	print "Content-type: text/html; charset=shift_jis\n\n";
	print $head;

	# �������O�W�J
	my ($flg,$word2,$date2);
	foreach (@log) {
		my ($no,$date,$word) = split(/<>/);
		if (!$flg) {
			$flg = 1;
			$word2 = $word;
			$date2 = $date;
			next;
		}

		my $tmp = $loop;
		$tmp =~ s/!date!/$date2/g;
		$tmp =~ s/!word-1!/$word/g;
		$tmp =~ s/!word-2!/$word2/g;
		print $tmp;

		$word2 = $word;
		$date2 = $date;
	}

	# �t�b�^
	footer($foot);
}

#-----------------------------------------------------------
#  ���ӎ����\��
#-----------------------------------------------------------
sub note_page {
	open(IN,"$cf{tmpldir}/note.html") or error("open err: note.html");
	my $tmpl = join('', <IN>);
	close(IN);

	# �����u������
	$tmpl =~ s/!term!/$cf{term}/g;
	$tmpl =~ s/!limit!/$cf{limit}/g;
	$tmpl =~ s|!icon:(\w+\.\w+)!|<img src="$cf{iconurl}/$1" alt="" />|g;

	print "Content-type: text/html; charset=shift_jis\n\n";
	print $tmpl;
	exit;
}

#-----------------------------------------------------------
#  �{���̉^��
#-----------------------------------------------------------
sub kuji_page {
	# ���t�擾
	my $date = get_time("cook");

	# �N�b�L�[�擾
	my ($date2,$rand1,$rand2) = get_cookie();

	# 24���Ԉȓ��̃N�b�L�[���Ȃ��ꍇ
	my $cookie;
	if ($date != $date2) {

		# �����𔭐�
		$rand1 = int(rand(@{$cf{kuji}}));
		$rand2 = int(rand(@{$cf{color}}));

		# �N�b�L�[�i�[
		set_cookie($date,$rand1,$rand2);
	}

	# ���������b�Z�[�W
	my ($kuji,$msg) = split(/,/,$cf{kuji}[$rand1]);
	
	# �F
	my ($text,$col) = split(/,/,$cf{color}[$rand2]);

	open(IN,"$cf{tmpldir}/kuji.html") or error("open err: kuji.html");
	my $tmpl = join('', <IN>);
	close(IN);

	# �����u������
	$tmpl =~ s/!kuji!/$kuji/g;
	$tmpl =~ s/!message!/$msg/g;
	$tmpl =~ s|!color!|<span style="color:$col">$text</span>|g;
	$tmpl =~ s|!icon:(\w+\.\w+)!|<img src="$cf{iconurl}/$1" alt="" />|g;

	print "Content-type: text/html; charset=shift_jis\n\n";
	print $tmpl;
	exit;
}

#-----------------------------------------------------------
#  �t�b�^�[
#-----------------------------------------------------------
sub footer {
	my $foot = shift;

	# ���쌠�\�L�i�폜�E���ϋ֎~�j
	my $copy = <<EOM;
<p style="margin-top:2.5em;text-align:center;font-family:Verdana,Helvetica,Arial;font-size:10px;">
	- <a href="http://www.kent-web.com/" target="_top">Monkey Banana</a> -
</p>
EOM

	if ($foot =~ /(.+)(<\/body[^>]*>.*)/si) {
		print "$1$copy$2\n";
	} else {
		print "$foot$copy\n";
		print "</body></html>\n";
	}
	exit;
}

#-----------------------------------------------------------
#  �G���[���
#-----------------------------------------------------------
sub error {
	my $err = shift;

	open(IN,"$cf{tmpldir}/error.html") or die;
	my $tmpl = join('', <IN>);
	close(IN);

	$tmpl =~ s/!error!/$err/g;
	$tmpl =~ s|!icon:(\w+\.\w+)!|<img src="$cf{iconurl}/$1" alt="error" />|g;

	print "Content-type: text/html; charset=shift_jis\n\n";
	print $tmpl;
	exit;
}

#-----------------------------------------------------------
#  �z�X�g�`�F�b�N
#-----------------------------------------------------------
sub host_chk {
	# �z�X�g���擾
	my $host = $ENV{REMOTE_HOST};
	my $addr = $ENV{REMOTE_ADDR};

	if ($cf{gethostbyaddr} && ($host eq "" || $host eq $addr)) {
		$host = gethostbyaddr(pack("C4", split(/\./, $addr)), 2);
	}
	if ($host eq "") { $host = $addr; }

	my $flg;
	foreach ( split(/\s+/,$cf{deny}) ) {
		s/\*/\.\*/g;
		if ($host =~ /$_/i) { $flg++; last; }
	}
	if ($flg) { error("���Ȃ��̃z�X�g�̓A�N�Z�X���ł��܂���"); }

	return $host;
}

#-----------------------------------------------------------
#  �֎~���[�h�`�F�b�N
#-----------------------------------------------------------
sub word_chk {
	my ($word) = @_;

	# �������`�F�b�N
	if ($word eq '') { error("���t�����͂���Ă��܂���"); }
	if (length($word) > $cf{limit} * 2) {
		error("�S�p��$cf{limit}�����𒴂��錾�t�͓o�^�ł��܂���");
	}

	# �֎~���[�h
	my $flg;
	foreach ( split(/\s+/,$cf{denyword}) ) {
		next if ($_ eq '');

		if (index($word,$_) >= 0) { $flg++; last; }
	}
	if ($flg) { error("�g�p�ł��Ȃ����t���܂܂�Ă��܂�"); }
}

#-----------------------------------------------------------
#  ���Ԏ擾
#-----------------------------------------------------------
sub get_time {
	my $key = shift;

	# ���Ԏ擾
	my ($sec,$min,$hour,$mday,$mon,$year) = (localtime(time))[0..5];

	# �����̃t�H�[�}�b�g
	if ($key eq "cook") {
		sprintf("%04d%02d%02d", $year+1900,$mon+1,$mday);
	} else {
		sprintf("%02d/%02d-%02d:%02d:%02d", $mon+1,$mday,$hour,$min,$sec);
	}
}

#-----------------------------------------------------------
#  �J�E���^����
#-----------------------------------------------------------
sub count_log {
	# IP�擾
	my $addr = $ENV{REMOTE_ADDR};

	# �{�����̂݃J�E���g�A�b�v
	my $cntup = $in{mode} eq '' ? 1 : 0;

	# �J�E���g�t�@�C����ǂ݂���
	open(LOG,"+< $cf{cntfile}") or error("open err: $cf{cntfile}");
	eval "flock(LOG, 2);";
	my $count = <LOG>;

	# IP�`�F�b�N�ƃ��O�j���`�F�b�N
	my ($cnt,$ip) = split(/:/,$count);
	if ($addr eq $ip or $cnt eq "") { $cntup = 0; }

	# �J�E���g�A�b�v
	if ($cntup) {
		$cnt++;
		seek(LOG, 0, 0);
		print LOG "$cnt:$addr";
		truncate(LOG, tell(LOG));
	}
	close(LOG);

	# ��������
	while(length($cnt) < $cf{mini_fig}) { $cnt = '0' . $cnt; }
	my @cnts = split(//, $cnt);

	# GIF�J�E���^�\��
	my $count;
	if ($cf{counter} == 2) {
		foreach (0 .. $#cnts) {
			$count .= qq|<img src="$cf{iconurl}/$cnts[$_].gif" alt="$cnts[$_]" />|;
		}

	# �e�L�X�g�J�E���^�\��
	} else {
		$count = qq|<span style="color:$cf{cntcol};font-family:Verdana,Helvetica,Arial">$cnt</span>\n|;
	}
	return $count;
}

#-----------------------------------------------------------
#  �N�b�L�[���s
#-----------------------------------------------------------
sub set_cookie {
	my @data = @_;

	my ($sec,$min,$hour,$mday,$mon,$year,$wday,undef,undef) = gmtime(time + 60*24*60*60);
	my @mon  = qw|Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec|;
	my @week = qw|Sun Mon Tue Wed Thu Fri Sat|;

	# �����t�H�[�}�b�g
	my $gmt = sprintf("%s, %02d-%s-%04d %02d:%02d:%02d GMT",
				$week[$wday],$mday,$mon[$mon],$year+1900,$hour,$min,$sec);

	# URL�G���R�[�h
	my $cook;
	foreach (@data) {
		s/(\W)/sprintf("%%%02X", unpack("C", $1))/eg;
		$cook .= "$_<>";
	}

	print "Set-Cookie: $cf{cookie_id}=$cook; expires=$gmt\n";
}

#-----------------------------------------------------------
#  �N�b�L�[�擾
#-----------------------------------------------------------
sub get_cookie {
	# �N�b�L�[�擾
	my $cook = $ENV{HTTP_COOKIE};

	# �Y��ID�����o��
	my %cook;
	foreach ( split(/;/,$cook) ) {
		my ($key,$val) = split(/=/);
		$key =~ s/\s//g;
		$cook{$key} = $val;
	}

	# URL�f�R�[�h
	my @cook;
	foreach ( split(/<>/,$cook{$cf{cookie_id}}) ) {
		s/%([0-9A-Fa-f][0-9A-Fa-f])/pack("H2", $1)/eg;
		s/[&"'<>]//g;

		push(@cook,$_);
	}
	return @cook;
}

