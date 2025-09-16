#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ MONKEY BANMANA : admin.cgi - 23014/11/08
#│ copyright (c) KentWeb
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

# 認証
check_passwd();

# 管理モード
admin_mode();

#-----------------------------------------------------------
#  管理モード
#-----------------------------------------------------------
sub admin_mode {
	# 削除
	if ($in{del}) {
		my %del;
		foreach ( split(/\0/,$in{del}) ) {
			$del{$_}++;
		}

		my @log;
		open(DAT,"+< $cf{logfile}") or error("open err: $cf{logfile}");
		eval "flock(DAT, 2);";
		while (<DAT>) {
			my ($no) = (split(/<>/))[0];

			if (!defined($del{$no})) { push(@log,$_); }
		}

		# 更新
		seek(DAT, 0, 0);
		print DAT @log;
		truncate(DAT, tell(DAT));
		close(DAT);
	}

	# 管理画面
	header("管理モード");
	print <<"EOM";
<div align="right">
<form action="$cf{monkey_cgi}">
<input type="submit" value="初期画面">
<input type="button" value="ログオフ" onclick=window.open("$cf{admin_cgi}","_top")>
</form>
</div>
<div class="ttl">■ 管理画面</div>
<ul>
<li>削除する記事にチェックを入れて「削除する」を押してください。
</ul>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="submit" value="削除する">
<dl class="list">
EOM

	# 記事を展開
	open(IN,"$cf{logfile}") or error("open err $cf{logfile}");
	while (<IN>) {
		my ($no,$date,$wd,$agent,$host) = split(/<>/);

		print qq|<dt><input type="checkbox" name="del" value="$no"> |;
		print qq|$date &nbsp; <b>$wd</b> - $agent</dt>\n|;
		print qq|<dd>HOST : $host</dd>\n|;
	}
	close(IN);

	print <<EOM;
</dl>
</form>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  HTMLヘッダー
#-----------------------------------------------------------
sub header {
	my $ttl = shift;

	print <<EOM;
Content-type: text/html; charset=shift_jis

<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=shift_jis">
<meta http-equiv="content-style-type" content="text/css">
<style type="text/css">
<!--
body,td,th { font-size:80%; background:#f0f0f0; }
div.ttl { border-bottom:1px solid #663300; color:#663300; padding:4px; font-weight:bold; }
p.err { color:#dd0000; }
dl.list dt { border-top:1px dotted #663300; padding:4px; margin-top:10px; }
dl.list b { color: green; }
-->
</style>
<title>$ttl</title>
</head>
<body>
EOM
}

#-----------------------------------------------------------
#  パスワード認証
#-----------------------------------------------------------
sub check_passwd {
	# パスワードが未入力の場合は入力フォーム画面
	if ($in{pass} eq "") {
		&enter_form;

	# パスワード認証
	} elsif ($in{pass} ne $cf{password}) {
		&error("認証できません");
	}
}

#-----------------------------------------------------------
#  入室画面
#-----------------------------------------------------------
sub enter_form {
	&header("入室画面");
	print <<EOM;
<div align="center">
<form action="$cf{admin_cgi}" method="post">
<table width="380" style="margin-top:50px">
<tr>
	<td height="40" align="center">
		<fieldset><legend>パスワード入力</legend><br>
		<input type="password" name="pass" value="" size="20">
		<input type="submit" value=" 認証 "><br><br>
		</fieldset>
	</td>
</tr>
</table>
</form>
<script language="javascript">
<!--
self.document.forms[0].pass.focus();
//-->
</script>
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  エラー
#-----------------------------------------------------------
sub error {
	my $err = shift;

	&header("ERROR!");
	print <<EOM;
<div align="center">
<hr width="350">
<h3>ERROR!</h3>
<p class="err">$err</p>
<hr width="350">
<form>
<input type="button" value="前画面に戻る" onclick="history.back()">
</form>
</div>
</body>
</html>
EOM
	exit;
}

