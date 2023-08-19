use strict;
use warnings;

my(@tables_) = (
	"analytics_fillstate",
	"analytics_installationcount",
	"analytics_realmcount",
	"analytics_streamcount",
	"analytics_usercount",
	"auth_group",
	"auth_group_permissions",
	"auth_permission",
	"confirmation_confirmation",
	"confirmation_realmcreationkey",
	"django_content_type",
	"django_migrations",
	"django_session",
	"fts_update_log",
	"otp_static_staticdevice",
	"otp_static_statictoken",
	"otp_totp_totpdevice",
	"social_auth_association",
	"social_auth_code",
	"social_auth_nonce",
	"social_auth_partial",
	"social_auth_usersocialauth",
	"third_party_api_results",
	"two_factor_phonedevice",
	"zerver_alertword",
	"zerver_archivedattachment",
	"zerver_archivedattachment_messages",
	"zerver_archivedmessage",
	"zerver_archivedreaction",
	"zerver_archivedsubmessage",
	"zerver_archivedusermessage",
	"zerver_archivetransaction",
	"zerver_attachment",
	"zerver_attachment_messages",
	"zerver_attachment_scheduled_messages",
	"zerver_botconfigdata",
	"zerver_botstoragedata",
	"zerver_client",
	"zerver_customprofilefield",
	"zerver_customprofilefieldvalue",
	"zerver_defaultstream",
	"zerver_defaultstreamgroup",
	"zerver_defaultstreamgroup_streams",
	"zerver_draft",
	"zerver_emailchangestatus",
	"zerver_groupgroupmembership",
	"zerver_huddle",
	"zerver_message",
	"zerver_missedmessageemailaddress",
	"zerver_multiuseinvite",
	"zerver_multiuseinvite_streams",
	"zerver_muteduser",
	"zerver_preregistrationrealm",
	"zerver_preregistrationuser",
	"zerver_preregistrationuser_streams",
	"zerver_pushdevicetoken",
	"zerver_reaction",
	"zerver_realm",
	"zerver_realmauditlog",
	"zerver_realmauthenticationmethod",
	"zerver_realmdomain",
	"zerver_realmemoji",
	"zerver_realmfilter",
	"zerver_realmplayground",
	"zerver_realmreactivationstatus",
	"zerver_realmuserdefault",
	"zerver_recipient",
	"zerver_scheduledemail",
	"zerver_scheduledemail_users",
	"zerver_scheduledmessage",
	"zerver_scheduledmessagenotificationemail",
	"zerver_service",
	"zerver_stream",
	"zerver_submessage",
	"zerver_subscription",
	"zerver_useractivity",
	"zerver_useractivityinterval",
	"zerver_usergroup",
	"zerver_usergroupmembership",
	"zerver_userhotspot",
	"zerver_usermessage",
	"zerver_userpresence",
	"zerver_userprofile",
	"zerver_userprofile_groups",
	"zerver_userprofile_user_permissions",
	"zerver_userstatus",
	"zerver_usertopic");

my(@tables) = ("zerver_recipient", "zerver_userprofile", "zerver_message");

my($filename) = "../../zulip.sql";
my($filename1) = "../../zulip.sql.1";

# TODO Launch ../install/bin/postgres -O -P -D ../../postgresql14_cc4baf5/data  -c log_error_verbosity=verbose

my($pipe) = ">";
for my $table (@tables)
{
	my($cmd) = "../install/bin/pg_dump --column-inserts --data-only --table=$table -U zulip zulip $pipe$filename1";
	print "$cmd\n";
	system($cmd);
	$pipe = ">>";
}

open my $file, '>', $filename or die "Could not open $filename: $!";
open my $file1, $filename1 or die "Could not open $filename1: $!";
while (my $line = <$file1>)
{
    if ($line =~ m/^INSERT.*$/)
    {
    	$line =~ s/\);/\) ON CONFLICT DO NOTHING;/g;
    }
    print $file "$line";
}

close $file;
close $file1;

system("rm -rf ../../postgresql14_cc4baf5");
system("cd ../.. && tar xf postgresql14_cc4baf5.tar.gz");

