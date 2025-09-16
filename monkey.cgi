#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ MONKEY BANANA : monkey.cgi - 2014/11/08
#│ copyright (c) KentWeb, 1997-2014
#│ http://www.kent-web.com/
#└─────────────────────────────────

# モジュール宣言
use strict;
use CGI::Carp qw(fatalsToBrowser);

# 設定ファイル認識
require "./init.cgi";
my %cf = set_init();

# データ受理
my %in = parse_form();

# 処理分岐
if ($in{mode} eq 'bana') { bana_data(); }
if ($in{mode} eq 'note') { note_page(); }
if ($in{mode} eq 'kuji') { kuji_page(); }
menu_list();

#-----------------------------------------------------------
#  メニュー画面
#-----------------------------------------------------------
sub menu_list {
	# カウンタ
	my $counter = count_log() if ($cf{counter});

	# トップ記事読み込み
	open(IN,"$cf{logfile}") or error("open err: $cf{logfile}");
	my $top = <IN>;
	close(IN);

	# トップ記事分解
	my ($num,$word) = (split(/<>/,$top))[0,2];
	$num  ||= 1;
	$word ||= "オサル";

	# テンプレート読み込み
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

	# ヘッダ表示
	print "Content-type: text/html; charset=shift_jis\n\n";
	footer($tmpl);
}

#-----------------------------------------------------------
#  記事受付
#-----------------------------------------------------------
sub bana_data {
	# ホストを取得
	my $host = host_chk();

	# ワードチェック
	word_chk($in{word});

	open(DAT,"+< $cf{logfile}") or error("open err: $cf{logfile}");
	eval "flock(DAT, 2);";
	my $top = <DAT>;

	my ($no,$date,$word,$agent,$hos,$tim);
	if ($top eq "") {
		$top = "1<>$date<>オサル<>local<>local<><>\n";
		$no = 1;
	} else {
		($no,$date,$word,$agent,$hos,$tim) = split(/<>/,$top);
	}

	# 同一ホストからの投稿は一定間隔の秒数をおく
	my $time = time;
	if ($host eq $hos && $time - $tim < $cf{term}) {
		close(DAT);
		error("連続登録は$cf{term}秒以上待ってね");
	}

	# １つ前の言葉をチェック
	if ($in{no} != $no) {
		close(DAT);
		error("残念、誰かが先に連想してしまったようです。<br />前画面に戻って再読み込みして下さい");
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
		error("残念、誰かが同じ言葉を連想したようです。<br />前画面に戻って他の言葉を連想し直してみてください");
	}

	# 記事NOを採番・時間を取得
	$no++;
	my $date = get_time();

	# ブラウザ情報
	my $hua = $ENV{HTTP_USER_AGENT};
	$hua =~ s/&/&amp;/g;
	$hua =~ s/</&lt;/g;
	$hua =~ s/>/&gt;/g;
	$hua =~ s/"/&quot;/g;

	# ログを更新
	unshift(@log,"$no<>$date<>$in{word}<>$hua<>$host<>$time<>\n");
	seek(DAT, 0, 0);
	print DAT @log;
	truncate(DAT, tell(DAT));
	close(DAT);

	# テンプレート読み込み
	open(IN,"$cf{tmpldir}/word.html") or error("open err: word.html");
	my $tmpl = join('', <IN>);
	close(IN);

	# 文字置き換え
	$tmpl =~ s|!icon:(\w+\.\w+)!|<img src="$cf{iconurl}/$1" alt="" />|g;
	$tmpl =~ s/!cgi_title!/$cf{cgi_title}/g;
	$tmpl =~ s/!monkey_cgi!/$cf{monkey_cgi}/g;

	# テンプレート分割
	my ($head,$loop,$foot) = $tmpl =~ /(.+)<!-- loop_begin -->(.+)<!-- loop_end -->(.+)/s
			? ($1,$2,$3)
			: error("テンプレート不正");

	# 画面表示
	print "Content-type: text/html; charset=shift_jis\n\n";
	print $head;

	# 履歴ログ展開
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

	# フッタ
	footer($foot);
}

#-----------------------------------------------------------
#  留意事項表示
#-----------------------------------------------------------
sub note_page {
	open(IN,"$cf{tmpldir}/note.html") or error("open err: note.html");
	my $tmpl = join('', <IN>);
	close(IN);

	# 文字置き換え
	$tmpl =~ s/!term!/$cf{term}/g;
	$tmpl =~ s/!limit!/$cf{limit}/g;
	$tmpl =~ s|!icon:(\w+\.\w+)!|<img src="$cf{iconurl}/$1" alt="" />|g;

	print "Content-type: text/html; charset=shift_jis\n\n";
	print $tmpl;
	exit;
}

#-----------------------------------------------------------
#  本日の運勢
#-----------------------------------------------------------
sub kuji_page {
	# 日付取得
	my $date = get_time("cook");

	# クッキー取得
	my ($date2,$rand1,$rand2) = get_cookie();

	# 24時間以内のクッキーがない場合
	my $cookie;
	if ($date != $date2) {

		# 乱数を発生
		$rand1 = int(rand(@{$cf{kuji}}));
		$rand2 = int(rand(@{$cf{color}}));

		# クッキー格納
		set_cookie($date,$rand1,$rand2);
	}

	# くじ＆メッセージ
	my ($kuji,$msg) = split(/,/,$cf{kuji}[$rand1]);
	
	# 色
	my ($text,$col) = split(/,/,$cf{color}[$rand2]);

	open(IN,"$cf{tmpldir}/kuji.html") or error("open err: kuji.html");
	my $tmpl = join('', <IN>);
	close(IN);

	# 文字置き換え
	$tmpl =~ s/!kuji!/$kuji/g;
	$tmpl =~ s/!message!/$msg/g;
	$tmpl =~ s|!color!|<span style="color:$col">$text</span>|g;
	$tmpl =~ s|!icon:(\w+\.\w+)!|<img src="$cf{iconurl}/$1" alt="" />|g;

	print "Content-type: text/html; charset=shift_jis\n\n";
	print $tmpl;
	exit;
}

#-----------------------------------------------------------
#  フッター
#-----------------------------------------------------------
sub footer {
	my $foot = shift;

	# 著作権表記（削除・改変禁止）
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
#  エラー画面
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
#  ホストチェック
#-----------------------------------------------------------
sub host_chk {
	# ホスト名取得
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
	if ($flg) { error("あなたのホストはアクセスができません"); }

	return $host;
}

#-----------------------------------------------------------
#  禁止ワードチェック
#-----------------------------------------------------------
sub word_chk {
	my ($word) = @_;

	# 文字数チェック
	if ($word eq '') { error("言葉が入力されていません"); }
	if (length($word) > $cf{limit} * 2) {
		error("全角で$cf{limit}文字を超える言葉は登録できません");
	}

	# 禁止ワード
	my $flg;
	foreach ( split(/\s+/,$cf{denyword}) ) {
		next if ($_ eq '');

		if (index($word,$_) >= 0) { $flg++; last; }
	}
	if ($flg) { error("使用できない言葉が含まれています"); }
}

#-----------------------------------------------------------
#  時間取得
#-----------------------------------------------------------
sub get_time {
	my $key = shift;

	# 時間取得
	my ($sec,$min,$hour,$mday,$mon,$year) = (localtime(time))[0..5];

	# 日時のフォーマット
	if ($key eq "cook") {
		sprintf("%04d%02d%02d", $year+1900,$mon+1,$mday);
	} else {
		sprintf("%02d/%02d-%02d:%02d:%02d", $mon+1,$mday,$hour,$min,$sec);
	}
}

#-----------------------------------------------------------
#  カウンタ処理
#-----------------------------------------------------------
sub count_log {
	# IP取得
	my $addr = $ENV{REMOTE_ADDR};

	# 閲覧時のみカウントアップ
	my $cntup = $in{mode} eq '' ? 1 : 0;

	# カウントファイルを読みこみ
	open(LOG,"+< $cf{cntfile}") or error("open err: $cf{cntfile}");
	eval "flock(LOG, 2);";
	my $count = <LOG>;

	# IPチェックとログ破損チェック
	my ($cnt,$ip) = split(/:/,$count);
	if ($addr eq $ip or $cnt eq "") { $cntup = 0; }

	# カウントアップ
	if ($cntup) {
		$cnt++;
		seek(LOG, 0, 0);
		print LOG "$cnt:$addr";
		truncate(LOG, tell(LOG));
	}
	close(LOG);

	# 桁数調整
	while(length($cnt) < $cf{mini_fig}) { $cnt = '0' . $cnt; }
	my @cnts = split(//, $cnt);

	# GIFカウンタ表示
	my $count;
	if ($cf{counter} == 2) {
		foreach (0 .. $#cnts) {
			$count .= qq|<img src="$cf{iconurl}/$cnts[$_].gif" alt="$cnts[$_]" />|;
		}

	# テキストカウンタ表示
	} else {
		$count = qq|<span style="color:$cf{cntcol};font-family:Verdana,Helvetica,Arial">$cnt</span>\n|;
	}
	return $count;
}

#-----------------------------------------------------------
#  クッキー発行
#-----------------------------------------------------------
sub set_cookie {
	my @data = @_;

	my ($sec,$min,$hour,$mday,$mon,$year,$wday,undef,undef) = gmtime(time + 60*24*60*60);
	my @mon  = qw|Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec|;
	my @week = qw|Sun Mon Tue Wed Thu Fri Sat|;

	# 時刻フォーマット
	my $gmt = sprintf("%s, %02d-%s-%04d %02d:%02d:%02d GMT",
				$week[$wday],$mday,$mon[$mon],$year+1900,$hour,$min,$sec);

	# URLエンコード
	my $cook;
	foreach (@data) {
		s/(\W)/sprintf("%%%02X", unpack("C", $1))/eg;
		$cook .= "$_<>";
	}

	print "Set-Cookie: $cf{cookie_id}=$cook; expires=$gmt\n";
}

#-----------------------------------------------------------
#  クッキー取得
#-----------------------------------------------------------
sub get_cookie {
	# クッキー取得
	my $cook = $ENV{HTTP_COOKIE};

	# 該当IDを取り出す
	my %cook;
	foreach ( split(/;/,$cook) ) {
		my ($key,$val) = split(/=/);
		$key =~ s/\s//g;
		$cook{$key} = $val;
	}

	# URLデコード
	my @cook;
	foreach ( split(/<>/,$cook{$cf{cookie_id}}) ) {
		s/%([0-9A-Fa-f][0-9A-Fa-f])/pack("H2", $1)/eg;
		s/[&"'<>]//g;

		push(@cook,$_);
	}
	return @cook;
}

