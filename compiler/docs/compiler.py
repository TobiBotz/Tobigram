#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

import ast
import os
import re
import shutil

from pyrogram import types as pyrogram_types

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HOME = os.path.join(ROOT, "compiler/docs")
DESTINATION = os.path.join(ROOT, "docs/source/telegram")
PYROGRAM_API_DEST = os.path.join(ROOT, "docs/source/api")

FUNCTIONS_PATH = os.path.join(ROOT, "pyrogram/raw/functions")
TYPES_PATH = os.path.join(ROOT, "pyrogram/raw/types")
BASE_PATH = os.path.join(ROOT, "pyrogram/raw/base")

FUNCTIONS_BASE = "functions"
TYPES_BASE = "types"
BASE_BASE = "base"


def snek(s: str):
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", s)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s).lower()


def generate(source_path, base):
    all_entities = {}

    def build(path, level=0):
        last = os.path.basename(path)

        for i in os.listdir(path):
            child = os.path.join(path, i)
            try:
                if not i.startswith("__"):
                    build(child, level=level + 1)
            except NotADirectoryError:
                with open(child, encoding="utf-8") as f:
                    p = ast.parse(f.read())

                for node in ast.walk(p):
                    if isinstance(node, ast.ClassDef):
                        name = node.name
                        break
                else:
                    continue

                full_path = os.path.basename(path) + "/" + snek(name).replace("_", "-") + ".rst"

                if level:
                    full_path = base + "/" + full_path

                namespace = os.path.basename(path)
                if namespace in ["base", "types", "functions"]:
                    namespace = ""

                full_name = f"{(namespace + '.') if namespace else ''}{name}"

                os.makedirs(os.path.dirname(os.path.join(DESTINATION, full_path)), exist_ok=True)

                with open(os.path.join(DESTINATION, full_path), "w", encoding="utf-8") as f:
                    f.write(
                        page_template.format(
                            title=full_name,
                            title_markup="=" * len(full_name),
                            full_class_path="pyrogram.raw.{}".format(
                                ".".join(full_path.split("/")[:-1]) + "." + name
                            ),
                        )
                    )

                if last not in all_entities:
                    all_entities[last] = []

                all_entities[last].append(name)

    build(source_path)

    for k, v in sorted(all_entities.items()):
        v = sorted(v)
        entities = []

        for i in v:
            entities.append(f"{i} <{snek(i).replace('_', '-')}>")

        if k != base:
            inner_path = base + "/" + k + "/index" + ".rst"
            module = f"pyrogram.raw.{base}.{k}"
        else:
            for i in sorted(all_entities, reverse=True):
                if i != base:
                    entities.insert(0, f"{i}/index")

            inner_path = base + "/index" + ".rst"
            module = f"pyrogram.raw.{base}"

        with open(os.path.join(DESTINATION, inner_path), "w", encoding="utf-8") as f:
            if k == base:
                f.write(":tocdepth: 1\n\n")
                k = "Raw " + k

            f.write(
                toctree.format(
                    title=k.title(),
                    title_markup="=" * len(k),
                    module=module,
                    entities="\n    ".join(entities),
                )
            )

            f.write("\n")


def pyrogram_api():
    def get_title_list(s: str) -> list:
        return [i.strip() for i in [j.strip() for j in s.split("\n") if j] if i]

    def is_property(bound_method: str) -> bool:
        cls_name, _, attr = bound_method.partition(".")
        return isinstance(getattr(getattr(pyrogram_types, cls_name, None), attr, None), property)

    # Methods

    categories = dict(
        account="""
        Account
            add_profile_audio
            cancel_password_email
            change_authorization_settings
            clear_recent_emoji_statuses
            confirm_bot_connection
            confirm_password_email
            confirm_phone
            create_theme
            decline_password_reset
            delete_account
            delete_auto_save_exceptions
            delete_passkey
            delete_secure_value
            delete_web_browser_settings_exceptions
            disable_peer_connected_bot
            edit_business_chat_link
            get_account_ttl
            get_all_secure_values
            get_authorization_form
            get_auto_download_settings
            get_auto_save_settings
            get_channel_default_emoji_statuses
            get_channel_restricted_status_emojis
            get_chat_themes
            get_collectible_emoji_statuses
            get_contact_sign_up_notification
            get_content_settings
            get_default_background_emojis
            get_default_group_photo_emojis
            get_default_profile_photo_emojis
            get_global_privacy_settings
            get_multi_wall_papers
            get_notify_exceptions
            get_notify_settings
            get_paid_messages_revenue
            get_passkeys
            get_password_settings
            get_privacy
            get_reactions_notify_settings
            get_recent_emoji_statuses
            get_saved_music_ids
            get_saved_ringtones
            get_secure_value
            get_theme
            get_themes
            get_tmp_password
            get_unique_gift_chat_themes
            get_wall_paper
            get_wall_papers
            get_web_authorizations
            get_web_browser_settings
            init_passkey_registration
            install_theme
            install_wall_paper
            invalidate_sign_in_codes
            register_device
            register_passkey
            remove_profile_audio
            reorder_usernames
            resend_password_email
            reset_notify_settings
            reset_password
            reset_wall_papers
            reset_web_authorization
            reset_web_authorizations
            save_auto_download_settings
            save_auto_save_settings
            save_ringtone
            save_secure_value
            save_theme
            save_wall_paper
            send_confirm_phone_code
            set_account_ttl
            set_contact_sign_up_notification
            set_content_settings
            set_global_privacy_settings
            set_inactive_session_ttl
            set_privacy
            set_profile_audio_position
            set_reactions_notify_settings
            toggle_connected_bot_paused
            toggle_no_paid_messages_exception
            toggle_sponsored_messages
            toggle_username
            toggle_web_browser_settings_exception
            unregister_device
            update_connected_bot
            update_device_locked
            update_theme
            update_web_browser_settings
            upload_ringtone
            upload_theme
            upload_wall_paper
            verify_phone
        """,
        advanced="""
        Advanced
            get_collectible_info
            get_file_hashes
            get_session
            get_web_file
            init_connection
            invoke
            invoke_after_msg
            invoke_after_msgs
            invoke_with_apns_secret
            invoke_with_google_play_integrity
            invoke_with_layer
            invoke_with_messages_range
            recover_gaps
            resolve_peer
            save_file
            set_dc
        """,
        aicompose="""
        AI Compose
            create_ai_tone
            delete_ai_tone
            get_ai_tone
            get_ai_tone_example
            get_ai_tones
            save_ai_tone
            update_ai_tone
        """,
        auth="""
        Authorization
            accept_login_token
            accept_terms_of_service
            bind_temp_auth_key
            cancel_code
            change_phone_number
            check_paid_auth
            check_password
            check_recovery_password
            connect
            disconnect
            drop_temp_auth_keys
            export_authorization
            export_login_token
            finish_firebase_pnv_login
            finish_passkey_login
            firebase_pnv_sign_up
            get_active_sessions
            get_password_hint
            import_authorization
            import_login_token
            import_web_token_authorization
            init_firebase_pnv_login
            init_passkey_login
            initialize
            log_out
            recover_password
            report_missing_code
            request_firebase_sms
            resend_code
            resend_phone_number_code
            reset_login_email
            reset_session
            reset_sessions
            send_code
            send_phone_number_code
            send_recovery_code
            sign_in
            sign_in_bot
            sign_up
            terminate
        """,
        bots="""
        Bots
            add_bot_preview_media
            allow_bot_send_message
            answer_callback_query
            answer_chat_join_request_query
            answer_guest_query
            answer_inline_query
            answer_pre_checkout_query
            answer_shipping_query
            answer_web_app_query
            answer_webhook_json_query
            can_bot_send_message
            check_bot_username
            check_download_file_params
            create_bot
            create_invoice_link
            delete_bot_commands
            delete_bot_preview_media
            edit_bot_preview_media
            edit_user_star_subscription
            get_admined_bots
            get_bot_commands
            get_bot_default_privileges
            get_bot_info
            get_bot_info_description
            get_bot_info_short_description
            get_bot_name
            get_bot_preview_info
            get_bot_preview_medias
            get_bot_recommendations
            get_chat_menu_button
            get_game_high_scores
            get_inline_bot_results
            get_managed_bot_access_settings
            get_managed_bot_token
            get_owned_bots
            get_popular_app_bots
            get_requested_web_view_button
            invoke_web_view_custom_method
            refund_star_payment
            reorder_bot_preview_medias
            reorder_bot_usernames
            replace_managed_bot_token
            request_callback_answer
            request_web_view_button
            send_chat_join_request_web_app
            send_custom_request
            send_game
            send_inline_bot_result
            send_invoice
            set_bot_commands
            set_bot_default_privileges
            set_bot_info_description
            set_bot_info_short_description
            set_bot_name
            set_chat_menu_button
            set_game_score
            set_managed_bot_access_settings
            toggle_bot_username
            toggle_user_emoji_status_permission
            update_star_ref_program
            update_user_emoji_status
        """,
        business="""
        Business
            create_business_chat_link
            delete_business_chat_link
            delete_business_messages
            get_business_account_gifts
            get_business_account_star_balance
            get_business_chat_links
            get_business_connection
            get_connected_bots
            read_business_message
            remove_business_account_profile_photo
            resolve_business_chat_link
            set_business_account_bio
            set_business_account_gift_settings
            set_business_account_name
            set_business_account_profile_photo
            set_business_account_username
            transfer_business_account_stars
            update_business_away_message
            update_business_greeting_message
            update_business_intro
            update_business_location
            update_business_work_hours
        """,
        chats="""
        Chats
            add_chat_members
            archive_chats
            ban_chat_member
            ban_chat_sender_chat
            close_forum_topic
            close_general_forum_topic
            convert_to_gigagroup
            create_channel
            create_forum_topic
            create_group
            create_supergroup
            deactivate_chat_usernames
            delete_all_message_reactions
            delete_channel
            delete_chat_photo
            delete_chat_sticker_set
            delete_forum_topic
            delete_message_reaction
            delete_supergroup
            delete_user_history
            edit_chat_location
            edit_forum_topic
            edit_general_forum_topic
            get_chat
            get_chat_event_log
            get_chat_member
            get_chat_members
            get_chat_members_count
            get_chat_online_count
            get_chat_settings
            get_dialogs
            get_dialogs_count
            get_direct_messages_topics
            get_direct_messages_topics_by_id
            get_forum_topic_icon_stickers
            get_forum_topics
            get_forum_topics_by_id
            get_inactive_channels
            get_left_channels
            get_nearby_chats
            get_personal_channels
            get_send_as_chats
            get_similar_channels
            get_suitable_discussion_chats
            get_top_chats
            hide_general_forum_topic
            join_chat
            leave_chat
            mark_chat_unread
            pin_chat_message
            pin_forum_topic
            promote_chat_member
            remove_chat_verification
            remove_user_verification
            reopen_forum_topic
            reopen_general_forum_topic
            reorder_chat_usernames
            reorder_pinned_forum_topics
            report_anti_spam_false_positive
            report_chat
            report_spam
            restrict_chat_member
            restrict_sponsored_messages
            set_administrator_title
            set_boosts_to_unblock_restrictions
            set_chat_accent_color
            set_chat_custom_emoji_sticker_set
            set_chat_description
            set_chat_direct_messages_group
            set_chat_discussion_group
            set_chat_member_tag
            set_chat_permissions
            set_chat_photo
            set_chat_protected_content
            set_chat_sticker_set
            set_chat_title
            set_chat_ttl
            set_chat_username
            set_main_profile_tab
            set_send_as_chat
            set_slow_mode
            set_upgraded_gift_colors
            toggle_anti_spam
            toggle_auto_translation
            toggle_chat_username
            toggle_forum
            toggle_join_request
            toggle_join_to_send
            toggle_participants_hidden
            toggle_pre_history_hidden
            toggle_signatures
            toggle_slow_mode
            toggle_view_forum_as_messages
            transfer_chat_ownership
            unarchive_chats
            unban_chat_member
            unban_chat_sender_chat
            unhide_general_forum_topic
            unpin_all_chat_messages
            unpin_all_forum_topic_messages
            unpin_all_general_forum_topic_messages
            unpin_chat_message
            unpin_forum_topic
            update_channel_color
            update_chat_notifications
            verify_chat
            verify_user
        """,
        communities="""
        Communities
            approve_community_link_request
            ban_community_participant
            collapse_community
            create_community
            get_community_link_requests
            get_joined_communities
            get_participant_joined_community_chats
            toggle_all_community_link_requests
            toggle_community_chat_link
        """,
        contacts="""
        Contacts
            accept_contact
            add_contact
            block_from_replies
            delete_contacts
            delete_contacts_by_phones
            edit_close_friends
            export_contact_token
            get_birthdays
            get_blocked_message_senders
            get_contact_ids
            get_contact_statuses
            get_contacts
            get_contacts_count
            get_saved_contacts
            get_sponsored_peers
            import_contact_token
            import_contacts
            reset_saved_contacts
            reset_top_peer_rating
            resolve_phone
            search_contacts
            set_blocked
            set_contact_note
            toggle_top_peers
            upload_contact_profile_photo
        """,
        ephemeral="""
        Ephemeral
            delete_all_welcome_messages
            delete_ephemeral_message
            delete_welcome_message
            edit_ephemeral_message_caption
            edit_ephemeral_message_media
            edit_ephemeral_message_reply_markup
            edit_ephemeral_message_text
            get_ephemeral_callback_answer
            get_welcome_messages
            report_ephemeral_message
            send_ephemeral_message
        """,
        folders="""
        Folders
            check_chat_folder_invite_link
            create_folder
            create_folder_invite_link
            delete_folder
            delete_folder_invite_link
            edit_folder
            edit_folder_invite_link
            get_chatlist_updates
            get_chats_for_folder_invite_link
            get_folder_invite_links
            get_folders
            get_leave_chatlist_suggestions
            hide_chatlist_updates
            join_chatlist_updates
            join_folder
            leave_folder
            reorder_folders
            toggle_folder_tags
        """,
        help="""
        Help
            dismiss_suggestion
            edit_user_info
            get_app_config
            get_app_update
            get_cdn_config
            get_countries_list
            get_deep_link_info
            get_invite_text
            get_nearest_dc
            get_passport_config
            get_peer_colors
            get_peer_profile_colors
            get_premium_promo
            get_promo_data
            get_recent_me_urls
            get_support
            get_support_name
            get_terms_of_service_update
            get_timezones_list
            get_user_info
            hide_promo_data
            save_app_log
            set_bot_updates_status
        """,
        invite_links="""
        Invite Links
            approve_all_chat_join_requests
            approve_chat_join_request
            create_chat_invite_link
            create_chat_subscription_invite_link
            decline_all_chat_join_requests
            decline_chat_join_request
            delete_chat_admin_invite_links
            delete_chat_invite_link
            edit_chat_invite_link
            edit_chat_subscription_invite_link
            export_chat_invite_link
            get_chat_admin_invite_links
            get_chat_admin_invite_links_count
            get_chat_admins_with_invite_links
            get_chat_invite_link
            get_chat_invite_link_joiners
            get_chat_invite_link_joiners_count
            get_chat_join_requests
            revoke_chat_invite_link
        """,
        langpack="""
        Language Pack
            get_difference
            get_lang_pack
            get_language
            get_languages
            get_strings
        """,
        listeners="""
        Listeners
            ask
            listen
            register_next_step_handler
            stop_listening
            wait_for_callback_query
            wait_for_message
        """,
        messages="""
        Messages
            add_checklist_tasks
            add_favorite_sticker
            add_poll_option
            add_to_gifs
            approve_suggested_post
            check_quick_reply_shortcut
            check_search_posts_flood
            clear_all_drafts
            clear_recent_reactions
            clear_recent_stickers
            click_sponsored_message
            compose_text_with_ai
            copy_media_group
            copy_message
            copy_messages
            decline_suggested_post
            delete_chat_history
            delete_direct_messages_chat_topic_history
            delete_fact_check
            delete_messages
            delete_participant_reaction
            delete_participant_reactions
            delete_poll_option
            delete_quick_reply_messages
            delete_quick_reply_shortcut
            delete_scheduled_messages
            download_media
            edit_fact_check
            edit_inline_caption
            edit_inline_media
            edit_inline_reply_markup
            edit_inline_text
            edit_message_caption
            edit_message_checklist
            edit_message_live_location
            edit_message_media
            edit_message_reply_markup
            edit_message_text
            edit_quick_reply_shortcut
            emojify_text_with_ai
            export_message_link
            fix_text_with_ai
            forward_media_group
            forward_messages
            get_all_drafts
            get_all_stickers
            get_archived_stickers
            get_available_effects
            get_available_reactions
            get_chat_history
            get_chat_history_count
            get_default_history_ttl
            get_default_tag_reactions
            get_direct_messages_chat_topic_history
            get_discussion_message
            get_discussion_replies
            get_discussion_replies_count
            get_emoji_stickers
            get_favorite_stickers
            get_featured_emoji_stickers
            get_featured_stickers
            get_main_web_app
            get_mask_stickers
            get_media_group
            get_message_author
            get_message_reactions
            get_message_read_participants
            get_messages
            get_messages_reactions
            get_paid_reaction_privacy
            get_poll_results
            get_poll_stats
            get_prepared_inline_message
            get_quick_replies
            get_quick_reply_messages
            get_recent_reactions
            get_recent_stickers
            get_rich_message
            get_saved_gifs
            get_saved_history
            get_saved_reaction_tags
            get_scheduled_messages
            get_search_results_calendar
            get_search_results_positions
            get_sponsored_messages
            get_top_reactions
            get_unread_reactions
            get_user_gifts
            get_user_personal_chat_messages
            get_user_profile_audios
            get_web_app_link_url
            get_web_app_url
            get_web_page
            get_web_page_preview
            gift_premium_subscription
            hide_peer_settings_bar
            mark_checklist_tasks_as_done
            open_web_app
            read_chat_history
            read_chat_message_contents
            read_featured_stickers
            read_mentions
            read_reactions
            read_saved_history
            reorder_pinned_dialogs
            reorder_quick_replies
            reorder_sticker_sets
            remove_favorite_sticker
            rephrase_text_with_ai
            report_messages
            report_reaction
            report_sponsored_message
            retract_vote
            save_draft
            save_prepared_inline_message
            save_prepared_keyboard_button
            save_recent_sticker
            search_global
            search_global_count
            search_messages
            search_messages_count
            search_posts
            search_posts_count
            send_animation
            send_audio
            send_cached_media
            send_chat_action
            send_checklist
            send_contact
            send_dice
            send_document
            send_live_photo
            send_location
            send_media_group
            send_message
            send_message_draft
            send_paid_media
            send_paid_reaction
            send_photo
            send_poll
            send_quick_reply_messages
            send_reaction
            send_rich_message
            send_rich_message_draft
            send_scheduled_messages
            send_screenshot_notification
            send_sticker
            send_venue
            send_video
            send_video_note
            send_voice
            set_chat_available_reactions
            set_chat_theme
            set_chat_wallpaper
            set_default_history_ttl
            set_default_reaction
            set_direct_messages_chat_topic_is_marked_as_unread
            set_passport_data_errors
            start_bot
            stop_message_live_location
            stop_poll
            stream_media
            summarize_text
            toggle_dialog_pin
            toggle_paid_reaction_privacy
            toggle_peer_translations
            toggle_saved_dialog_pin
            transcribe_audio
            translate_text
            update_saved_reaction_tag
            view_messages
            view_sponsored_message
            vote_poll
            get_attached_stickers
            get_dialog_unread_marks
            get_document_by_hash
            get_emoji_groups
            get_emoji_keywords
            get_emoji_keywords_difference
            get_emoji_keywords_languages
            get_emoji_profile_photo_groups
            get_emoji_sticker_groups
            get_emoji_status_groups
            get_emoji_url
            get_extended_media
            get_fact_check
            get_message_edit_data
            get_outbox_read_date
            get_pinned_saved_dialogs
            get_poll_votes
            get_recent_locations
            get_stickers_by_emoticon
            get_unread_mentions
            get_unread_poll_votes
            rate_transcribed_audio
            read_discussion
            read_poll_votes
            reorder_pinned_saved_dialogs
            report_messages_delivery
            search_custom_emoji
            search_emoji_sticker_sets
            search_sent_media
            search_sticker_sets
            search_stickers
            accept_url_auth
            check_url_auth_match_code
            decline_url_auth
            delete_chat
            delete_phone_call_history
            edit_chat_admin
            get_attach_menu_bot
            get_attach_menu_bots
            get_bot_app
            get_dh_config
            get_emoji_game_info
            get_future_chat_creator_after_leave
            get_old_featured_stickers
            get_split_ranges
            get_suggested_dialog_filters
            migrate_chat
            prolong_web_view
            read_message_contents
            received_messages
            received_queue
            report_music_listen
            report_read_metrics
            request_chat_join_web_view
            request_url_auth
            send_bot_requested_peer
            send_web_view_data
            toggle_bot_in_attach_menu
            toggle_sticker_sets
            translate_rich_message
            accept_encryption
            check_history_import
            check_history_import_peer
            discard_encryption
            init_history_import
            read_encrypted_history
            received_messages
            received_queue
            report_encrypted_spam
            request_encryption
            send_encrypted
            send_encrypted_file
            send_encrypted_service
            set_encrypted_typing
            start_history_import
            upload_encrypted_file
            upload_imported_media
            compose_rich_message_with_ai
        """,
        password="""
        Password
            change_cloud_password
            enable_cloud_password
            remove_cloud_password
        """,
        payments="""
        Payments
            add_collection_gifts
            apply_gift_code
            assign_app_store_transaction
            assign_play_market_transaction
            buy_gift_upgrade
            can_purchase_store
            check_can_send_gift
            check_gift_code
            clear_saved_info
            connect_star_ref_bot
            convert_gift_to_stars
            craft_gift
            create_gift_collection
            delete_gift_collection
            drop_gift_original_details
            edit_connected_star_ref_bot
            edit_star_subscription
            get_available_gifts
            get_bank_card_data
            get_chat_gifts
            get_chat_gifts_count
            get_connected_star_ref_bot
            get_connected_star_ref_bots
            get_gift_auction_state
            get_gift_collections
            get_gift_upgrade_preview
            get_gift_upgrade_variants
            get_gifts_for_crafting
            get_giveaway_info
            get_payment_form
            get_payment_receipt
            get_premium_gift_code_options
            get_received_gifts
            get_received_gifts_count
            get_saved_info
            get_saved_star_gift
            get_star_gift_active_auctions
            get_star_gift_auction_acquired_gifts
            get_star_gift_withdrawal_url
            get_stars_balance
            get_stars_gift_options
            get_stars_giveaway_options
            get_stars_revenue_ads_account_url
            get_stars_revenue_stats
            get_stars_revenue_withdrawal_url
            get_stars_subscriptions
            get_stars_topup_options
            get_stars_transactions
            get_stars_transactions_by_id
            get_suggested_star_ref_bots
            get_ton_balance
            get_upgraded_gift
            get_upgraded_gift_value_info
            gift_premium_with_stars
            hide_gift
            increase_gift_auction_bid
            launch_prepaid_giveaway
            place_gift_auction_bid
            process_gift_purchase_offer
            remove_collection_gifts
            reorder_collection_gifts
            reorder_gift_collections
            reuse_star_subscription
            search_gifts_for_resale
            send_gift
            send_gift_purchase_offer
            send_payment_form
            send_resold_gift
            set_gift_collection_name
            set_gift_resale_price
            set_pinned_gifts
            show_gift
            suggest_birthday
            toggle_chat_star_gift_notifications
            transfer_gift
            upgrade_gift
            validate_requested_info
        """,
        phone="""
        Phone
            get_call_members
        """,
        premium="""
        Premium
            apply_boost
            get_boosts
            get_boosts_list
            get_boosts_status
            get_user_boosts
        """,
        smsjobs="""
        SMS Jobs
            finish_sms_job
            get_sms_job
            get_sms_jobs_status
            is_eligible_to_join_sms_jobs
            join_sms_jobs
            leave_sms_jobs
            update_sms_jobs_settings
        """,
        stats="""
        Stats
            get_broadcast_stats
            get_megagroup_stats
            get_message_public_forwards
            get_message_stats
            get_story_public_forwards
            get_story_stats
            load_async_graph
        """,
        stickers="""
        Stickers
            add_favorite_sticker
            add_recent_sticker
            add_sticker_to_set
            change_sticker
            change_sticker_set
            check_sticker_set_name
            clear_recent_stickers
            create_new_sticker_set
            create_sticker_set
            delete_sticker_from_set
            delete_sticker_set
            get_custom_emoji_stickers
            get_favorite_stickers
            get_my_stickers
            get_owned_sticker_sets
            get_recent_stickers
            get_sticker_set
            get_stickers
            get_suggested_sticker_set_name
            remove_favorite_sticker
            remove_recent_sticker
            remove_sticker_from_set
            reorder_installed_sticker_sets
            replace_sticker
            replace_sticker_in_set
            save_sticker_set
            search_sticker_sets
            search_stickers
            set_custom_emoji_sticker_set_thumbnail
            set_sticker_emoji_list
            set_sticker_keywords
            set_sticker_mask_position
            set_sticker_position
            set_sticker_position_in_set
            set_sticker_set_thumb
            set_sticker_set_thumbnail
            set_sticker_set_title
            suggest_sticker_set_name
            unsave_sticker_set
            upload_sticker_file
        """,
        stories="""
        Stories
            can_post_stories
            copy_story
            copy_story_album
            create_story_album
            delete_stories
            delete_story_album
            edit_story_caption
            edit_story_media
            edit_story_privacy
            enable_stealth_mode
            export_story_link
            forward_story
            get_all_read_peer_stories
            get_all_stories
            get_archived_stories
            get_chat_stories
            get_chats_to_send_stories
            get_peer_max_story_ids
            get_pinned_stories
            get_stories
            get_stories_views
            get_story_album_stories
            get_story_albums
            get_story_reactions_list
            get_story_views
            hide_chat_stories
            pin_chat_stories
            read_chat_stories
            reorder_story_albums
            report_story
            search_stories
            send_story
            send_story_reaction
            show_chat_stories
            start_live_story
            toggle_all_stories_hidden
            toggle_stories_pinned_to_top
            unpin_chat_stories
            update_story_album
            view_stories
        """,
        users="""
        Users
            block_user
            check_username
            delete_profile_photos
            get_chat_audios
            get_chat_audios_count
            get_chat_photos
            get_chat_photos_count
            get_common_chats
            get_default_emoji_statuses
            get_me
            get_requirements_to_contact
            get_saved_music_by_id
            get_users
            report_profile_photo
            report_user
            set_bot_profile_photo
            set_emoji_status
            set_personal_channel
            set_profile_photo
            set_secure_value_errors
            set_username
            unblock_user
            update_birthday
            update_profile
            update_status
        """,
        utilities="""
        Utilities
            add_handler
            export_session_string
            ping
            remove_handler
            restart
            run
            set_parse_mode
            start
            stop
            stop_transmission
        """,
        decorators="""
        Decorators
            on_business_connection
            on_business_message
            on_callback_query
            on_chat_boost
            on_chat_join_request
            on_chat_left
            on_chat_member_updated
            on_chosen_inline_result
            on_connect
            on_deleted_business_messages
            on_deleted_messages
            on_disconnect
            on_edited_business_message
            on_edited_message
            on_error
            on_guest_message
            on_inline_query
            on_managed_bot
            on_message
            on_message_generation_stopped
            on_message_reaction
            on_message_reaction_count
            on_poll
            on_pre_checkout_query
            on_purchased_paid_media
            on_raw_update
            on_shipping_query
            on_start
            on_stop
            on_story
            on_user_status
        """,
    )

    root = PYROGRAM_API_DEST

    shutil.rmtree(os.path.join(root, "methods"), ignore_errors=True)
    os.makedirs(os.path.join(root, "methods"), exist_ok=True)

    with open(os.path.join(HOME, "template/methods.rst")) as f:
        template = f.read()

    with open(os.path.join(root, "methods/index.rst"), "w") as f:
        fmt_keys = {}

        for k, v in categories.items():
            name, *methods = get_title_list(v)
            fmt_keys.update({k: "\n    ".join(f"{m} <{m}>" for m in methods)})

            for method in methods:
                with open(os.path.join(root, f"methods/{method}.rst"), "w") as f2:
                    title = f"{method}()"

                    f2.write(title + "\n" + "=" * len(title) + "\n\n")
                    f2.write(f".. automethod:: pyrogram.Client.{method}()")

            functions = ["idle", "compose"]

            for func in functions:
                with open(os.path.join(root, f"methods/{func}.rst"), "w") as f2:
                    title = f"{func}()"

                    f2.write(title + "\n" + "=" * len(title) + "\n\n")
                    f2.write(f".. autofunction:: pyrogram.{func}()")

        f.write(template.format(**fmt_keys))

    # Types

    categories = dict(
        user_and_chats="""
        Users & Chats
            User
            Chat
            ChatPreview
            ChatPhoto
            ChatMember
            ChatPermissions
            ChatPrivileges
            ChatLocation
            ChatInviteLink
            ChatAdminWithInviteLinks
            ChatEvent
            ChatEventFilter
            ChatMemberUpdated
            ChatJoinRequest
            ChatJoiner
            Dialog
            Restriction
            EmojiStatus
            BackgroundFillFreeformGradient
            BackgroundFillGradient
            BackgroundFillSolid
            BackgroundTypeChatTheme
            BackgroundTypeFill
            BackgroundTypePattern
            BackgroundTypeWallpaper
            Birthday
            BusinessConnection
            BusinessIntro
            BusinessRecipients
            BusinessWorkingHours
            BusinessWeeklyOpen
            ChatAdministratorRights
            ChatColor
            ChatJoinResult
            ChatSettings
            Folder
            FolderInviteLink
            FoundContacts
            GlobalPrivacySettings
            GroupCallMember
            HistoryCleared
            InviteLinkImporter
            PhoneCallEnded
            PhoneCallStarted
            PrivacyRule
            StoriesStealthMode
            StoryAlbum
            ContactBirthday
            SavedPhoneContact
            UserRating
            AcceptedGiftTypes
            BotVerification
            BusinessBotRights
            ChatFolderInviteLinkInfo
            ChatFullInfo
            ChatJoinResultDeclined
            ChatJoinResultGuardBotApprovalRequired
            ChatJoinResultRequestSent
            ChatJoinResultSuccess
            Community
            CommunityChatAdded
            CommunityChatJoined
            CommunityChatRemoved
            FailedToAddMember
            Link
            Username
            VerificationStatus
        """,
        messages_media="""
        Messages & Media
            Message
            MessageEntity
            MessageGenerationStopped
            Photo
            Thumbnail
            Audio
            Document
            Animation
            Video
            VideoQuality
            Voice
            VideoNote
            Contact
            Location
            Venue
            Sticker
            StickerSet
            Game
            WebPage
            Poll
            PollOption
            Dice
            Reaction
            ReadParticipantDate
            VideoChatScheduled
            VideoChatStarted
            VideoChatEnded
            VideoChatMembersInvited
            WebAppData
            MessageReactions
            MessagePeerReaction
            ChatReactions
            AvailableEffect
            BoostsStatus
            BusinessMessage
            ChatBackground
            ChatBoost
            Checklist
            ChecklistTask
            ChecklistTasksAdded
            ChecklistTasksDone
            ContactRegistered
            DirectMessagePriceChanged
            DirectMessagesTopic
            EphemeralMessageParameters
            ExternalReplyInfo
            FactCheck
            FormattedText
            ForumTopic
            ForumTopicClosed
            ForumTopicCreated
            ForumTopicEdited
            ForumTopicReopened
            GeneralForumTopicHidden
            GeneralForumTopicUnhidden
            Gift
            GiftAttribute
            GiftBackground
            GiftAuction
            GiftAuctionState
            GiftCollection
            GiftedPremium
            GiftedStars
            GiftedGrams
            Giveaway
            GiveawayCompleted
            GiveawayCreated
            GiveawayPrizeStars
            GiveawayWinners
            InputChecklistTask
            Invoice
            LinkPreviewOptions
            LivePhoto
            ManagedBotCreated
            MaskPosition
            MediaArea
            MessageContent
            MessageOrigin
            MessageOriginChannel
            MessageOriginChat
            MessageOriginHiddenUser
            MessageOriginImport
            MessageOriginUser
            MyBoost
            PaidMediaInfo
            PaidMediaPreview
            PaidMessagesPriceChanged
            PaidMessagesRefunded
            PaidReactor
            PaymentForm
            PaymentOption
            PollOptionAdded
            PollOptionDeleted
            PremiumGiftCode
            ProximityAlertTriggered
            RefundedPayment
            ReplyParameters
            RestrictionReason
            RichBlock
            RichMessage
            RichMessageButton
            RichText
            ScreenshotTaken
            StarAmount
            StarsRevenueStats
            StarsRevenueStatus
            StarsTransaction
            Story
            StoryView
            StrippedThumbnail
            SuggestedPostApprovalFailed
            SuggestedPostApproved
            SuggestedPostDeclined
            SuggestedPostInfo
            SuggestedPostPaid
            SuggestedPostParameters
            SuggestedPostPrice
            SuggestedPostRefunded
            TextQuote
            TranscribedAudio
            UpgradedGiftAttributeId
            UpgradedGiftAttributeIdBackdrop
            UpgradedGiftAttributeIdModel
            UpgradedGiftAttributeIdSymbol
            UpgradedGiftAttributeRarity
            UpgradedGiftOriginalDetails
            UpgradedGiftPurchaseOffer
            UpgradedGiftValueInfo
            WriteAccessAllowed
            AuctionBid
            AuctionRound
            AuctionState
            AuctionStateActive
            AuctionStateFinished
            ChatHasProtectedContentDisableRequested
            ChatHasProtectedContentToggled
            ChatOwnerChanged
            ChatOwnerLeft
            ChatTheme
            CheckedGiftCode
            CraftGiftResult
            CraftGiftResultFail
            CraftGiftResultSuccess
            GiftPurchaseLimit
            GiftResaleParameters
            GiftResalePrice
            GiftResalePriceStar
            GiftResalePriceTon
            GiftUpgradePreview
            GiftUpgradePrice
            GiftUpgradeVariants
            PaymentResult
            PollStats
            RichBlockAnchor
            RichBlockAnimation
            RichBlockAudio
            RichBlockBlockQuotation
            RichBlockButtons
            RichBlockCaption
            RichBlockCollage
            RichBlockDetails
            RichBlockDivider
            RichBlockDocument
            RichBlockExpandableBlockQuotation
            RichBlockFooter
            RichBlockList
            RichBlockListItem
            RichBlockMap
            RichBlockMathematicalExpression
            RichBlockParagraph
            RichBlockPhoto
            RichBlockPreformatted
            RichBlockPullQuotation
            RichBlockSectionHeading
            RichBlockSlideshow
            RichBlockTable
            RichBlockTableCell
            RichBlockThinking
            RichBlockUnsupported
            RichBlockVideo
            RichBlockVoiceNote
            RichTextAnchor
            RichTextAnchorLink
            RichTextBankCardNumber
            RichTextBold
            RichTextButton
            RichTextBotCommand
            RichTextCashtag
            RichTextCode
            RichTextCustomEmoji
            RichTextDateTime
            RichTextDiff
            RichTextEmailAddress
            RichTextHashtag
            RichTextImage
            RichTextItalic
            RichTextMarked
            RichTextMathematicalExpression
            RichTextMention
            RichTextPhoneNumber
            RichTextReference
            RichTextReferenceLink
            RichTextSpoiler
            RichTextStrikethrough
            RichTextSubscript
            RichTextSuperscript
            RichTextTextMention
            RichTextUnderline
            RichTextUrl
            SavedCredentials
            Str
            SuccessfulPayment
            SuggestedPostPriceStar
            SuggestedPostPriceTon
            UpgradedGiftAttributeRarityEpic
            UpgradedGiftAttributeRarityLegendary
            UpgradedGiftAttributeRarityPerMille
            UpgradedGiftAttributeRarityRare
            UpgradedGiftAttributeRarityUncommon
            UpgradedGiftPurchaseOfferRejected
        """,
        bots_and_keyboards="""
        Bot keyboards
            ReplyKeyboardMarkup
            KeyboardButton
            ReplyKeyboardRemove
            InlineKeyboardMarkup
            InlineKeyboardButton
            CopyTextButton
            DisabledButton
            SwitchInlineQueryChosenChat
            LoginUrl
            ForceReply
            CallbackQuery
            GameHighScore
            CallbackGame
            WebAppInfo
            MenuButton
            MenuButtonCommands
            MenuButtonWebApp
            MenuButtonDefault
            SentWebAppMessage
            BotCommand
            BotCommandScope
            BotCommandScopeDefault
            BotCommandScopeAllPrivateChats
            BotCommandScopeAllGroupChats
            BotCommandScopeAllChatAdministrators
            BotCommandScopeChat
            BotCommandScopeChatAdministrators
            BotCommandScopeChatMember
            BotAccessSettings
            BotDescription
            BotName
            BotShortDescription
            ChatBoostUpdated
            ChatShared
            KeyboardButtonPollType
            KeyboardButtonRequestChat
            KeyboardButtonRequestManagedBot
            KeyboardButtonRequestUsers
            LabeledPrice
            ManagedBotUpdated
            MessageReactionCountUpdated
            MessageReactionUpdated
            OrderInfo
            PreCheckoutQuery
            PurchasedPaidMedia
            SentGuestMessage
            ShippingAddress
            ShippingOption
            ShippingQuery
            UsersShared
        """,
        inline_mode="""
        Inline Mode
            InlineQuery
            InlineQueryResult
            InlineQueryResultCachedAudio
            InlineQueryResultCachedDocument
            InlineQueryResultCachedAnimation
            InlineQueryResultCachedPhoto
            InlineQueryResultCachedSticker
            InlineQueryResultCachedVideo
            InlineQueryResultCachedVoice
            InlineQueryResultArticle
            InlineQueryResultAudio
            InlineQueryResultContact
            InlineQueryResultDocument
            InlineQueryResultAnimation
            InlineQueryResultLocation
            InlineQueryResultPhoto
            InlineQueryResultVenue
            InlineQueryResultVideo
            InlineQueryResultVoice
            ChosenInlineResult
        """,
        input_content="""
        Input Content
            InputMedia
            InputMediaPhoto
            InputMediaVideo
            InputMediaAudio
            InputMediaAnimation
            InputMediaDocument
            InputPhoneContact
            InputChatPhoto
            InputChecklist
            InputCredentials
            InputCredentialsApplePay
            InputCredentialsGooglePay
            InputCredentialsNew
            InputCredentialsSaved
            InputInvoice
            InputInvoiceMessage
            InputInvoiceMessageContent
            InputInvoiceName
            InputMediaLink
            InputMediaLivePhoto
            InputMediaLocation
            InputMediaSticker
            InputSticker
            InputMediaVenue
            InputMessageContent
            InputPollMedia
            InputPollOption
            InputPollOptionMedia
            InputPrivacyRule
            InputPrivacyRuleAllowAll
            InputPrivacyRuleAllowBots
            InputPrivacyRuleAllowChats
            InputPrivacyRuleAllowCloseFriends
            InputPrivacyRuleAllowContacts
            InputPrivacyRuleAllowPremium
            InputPrivacyRuleAllowUsers
            InputPrivacyRuleDisallowAll
            InputPrivacyRuleDisallowBots
            InputPrivacyRuleDisallowChats
            InputPrivacyRuleDisallowContacts
            InputPrivacyRuleDisallowUsers
            InputRichMessage
            InputRichMessageContent
            InputTextMessageContent
            InputContactMessageContent
            InputLocationMessageContent
            InputVenueMessageContent
            InputChatPhotoAnimation
            InputChatPhotoPrevious
            InputChatPhotoStatic
            InputMediaVoiceNote
            InputRichBlock
            InputRichBlockAnchor
            InputRichBlockAnimation
            InputRichBlockAudio
            InputRichBlockBlockQuotation
            InputRichBlockButtons
            InputRichBlockCollage
            InputRichBlockDetails
            InputRichBlockDivider
            InputRichBlockDocument
            InputRichBlockExpandableBlockQuotation
            InputRichBlockFooter
            InputRichBlockList
            InputRichBlockListItem
            InputRichBlockMap
            InputRichBlockMathematicalExpression
            InputRichBlockParagraph
            InputRichBlockPhoto
            InputRichBlockPreformatted
            InputRichBlockPullQuotation
            InputRichBlockSectionHeading
            InputRichBlockSlideshow
            InputRichBlockTable
            InputRichBlockTableCell
            InputRichBlockThinking
            InputRichBlockVideo
            InputRichBlockVoiceNote
            InputRichMessageMedia
        """,
        listeners="""
        Listeners
            Identifier
            Listener
        """,
        authorization="""
        Authorization
            SentCode
            TermsOfService
            ActiveSession
            ActiveSessions
            FirebaseAuthenticationSettings
            PhoneNumberAuthenticationSettings
            List
            FirebaseAuthenticationSettingsAndroid
            FirebaseAuthenticationSettingsIos
        """,
        enums="""
        Enums
            BlockAlignment
            BlockList
            BusinessSchedule
            ButtonStyle
            RichButtonStyle
            ChatAction
            ChatEventAction
            ChatJoinRequestQueryResult
            ListenerTypes
            ChatJoinType
            ChatMemberStatus
            ChatMembersFilter
            ChatType
            ClientPlatform
            FolderColor
            GiftAttributeType
            GiftForResaleOrder
            GiftPurchaseOfferState
            GiftType
            MaskPointType
            MediaAreaType
            MessageEntityType
            MessageMediaType
            MessageOriginType
            MessageServiceType
            MessagesFilter
            NextCodeType
            PaidReactionPrivacy
            ParseMode
            PaymentFormType
            PhoneCallDiscardReason
            PhoneNumberCodeType
            PollType
            PrivacyKey
            PrivacyRuleType
            ProfileColor
            ProfileTab
            ProxyScheme
            ReplyColor
            ReportReason
            SentCodeType
            StickerType
            StoriesPrivacyRules
            SuggestedPostRefundReason
            SuggestedPostState
            TopChatCategory
            UpgradedGiftOrigin
            UserStatus
        """,
    )

    root = PYROGRAM_API_DEST

    shutil.rmtree(os.path.join(root, "types"), ignore_errors=True)
    os.makedirs(os.path.join(root, "types"), exist_ok=True)

    with open(os.path.join(HOME, "template/types.rst")) as f:
        template = f.read()

    with open(os.path.join(root, "types/index.rst"), "w") as f:
        fmt_keys = {}

        for k, v in categories.items():
            name, *types = get_title_list(v)

            fmt_keys.update({k: "\n    ".join(types)})

            # noinspection PyShadowingBuiltins
            for type in types:
                with open(os.path.join(root, f"types/{type}.rst"), "w") as f2:
                    title = f"{type}"

                    f2.write(title + "\n" + "=" * len(title) + "\n\n")

                    if k == "enums":
                        f2.write(f".. autoclass:: pyrogram.enums.{type}()\n")
                        f2.write("    :members:\n")
                        f2.write("    :undoc-members:\n")
                    else:
                        f2.write(f".. autoclass:: pyrogram.types.{type}()\n")

        f.write(template.format(**fmt_keys))

    # Bound Methods

    categories = dict(
        message="""
        Message
            Message.click
            Message.delete
            Message.delete_ephemeral
            Message.edit_ephemeral_text
            Message.edit_ephemeral_caption
            Message.edit_ephemeral_media
            Message.edit_ephemeral_reply_markup
            Message.reply_ephemeral_text
            Message.download
            Message.forward
            Message.copy
            Message.copy_media_group
            Message.pin
            Message.unpin
            Message.edit
            Message.edit_text
            Message.edit_caption
            Message.edit_media
            Message.edit_reply_markup
            Message.reply
            Message.reply_text
            Message.reply_animation
            Message.reply_audio
            Message.reply_cached_media
            Message.reply_chat_action
            Message.reply_checklist
            Message.reply_contact
            Message.reply_dice
            Message.reply_document
            Message.reply_game
            Message.reply_inline_bot_result
            Message.reply_invoice
            Message.reply_live_photo
            Message.reply_location
            Message.reply_media_group
            Message.reply_paid_media
            Message.reply_photo
            Message.reply_poll
            Message.reply_rich
            Message.reply_sticker
            Message.reply_venue
            Message.reply_video
            Message.reply_video_note
            Message.reply_voice
            Message.answer
            Message.answer_animation
            Message.answer_audio
            Message.answer_cached_media
            Message.answer_checklist
            Message.answer_contact
            Message.answer_dice
            Message.answer_document
            Message.answer_game
            Message.answer_inline_bot_result
            Message.answer_invoice
            Message.answer_live_photo
            Message.answer_location
            Message.answer_media_group
            Message.answer_paid_media
            Message.answer_photo
            Message.answer_poll
            Message.answer_rich
            Message.answer_sticker
            Message.answer_venue
            Message.answer_video
            Message.answer_video_note
            Message.answer_voice
            Message.get_media_group
            Message.get_reactions
            Message.get_read_participants
            Message.react
            Message.report
            Message.wait_for_click
            Message.read
            Message.view
            Message.vote
            Message.pay
            Message.retract_vote
            Message.edit_checklist
            Message.edit_live_location
            Message.stop_live_location
            Message.summarize
            Message.transcribe
            Message.content
            Message.link
            Message.html_text
            Message.md_text
            Message.forward_date
            Message.forward_from
            Message.forward_from_chat
            Message.forward_from_message_id
            Message.forward_sender_name
            Message.forward_signature
            Message.is_topic_message
        """,
        chat="""
        Chat
            Chat.archive
            Chat.ask
            Chat.listen
            Chat.stop_listening
            Chat.unarchive
            Chat.set_title
            Chat.set_description
            Chat.set_photo
            Chat.ban_member
            Chat.unban_member
            Chat.restrict_member
            Chat.promote_member
            Chat.get_member
            Chat.get_members
            Chat.add_members
            Chat.join
            Chat.leave
            Chat.mark_unread
            Chat.set_protected_content
            Chat.unpin_all_messages
            Chat.report
            Chat.report_spam
            Chat.mute
            Chat.unmute
            Chat.set_ttl
            Chat.export_invite_link
            Chat.full_name
            Chat.is_fake
            Chat.is_scam
            Chat.is_verified
        """,
        user="""
        User
            User.archive
            User.unarchive
            User.block
            User.unblock
            User.full_name
            User.is_fake
            User.is_scam
            User.is_verified
            User.mention
            User.report
            User.get_common_chats
        """,
        callback_query="""
        Callback Query
            CallbackQuery.answer
            CallbackQuery.edit_message_text
            CallbackQuery.edit_message_caption
            CallbackQuery.edit_message_media
            CallbackQuery.edit_message_reply_markup
        """,
        inline_query="""
        InlineQuery
            InlineQuery.answer
        """,
        chat_join_request="""
        ChatJoinRequest
            ChatJoinRequest.approve
            ChatJoinRequest.decline
        """,
        story="""
        Story
            Story.copy
            Story.delete
            Story.download
            Story.edit_caption
            Story.edit_media
            Story.edit_privacy
            Story.forward
            Story.link
            Story.react
            Story.read
            Story.report
            Story.view
            Story.reply_text
            Story.reply_animation
            Story.reply_audio
            Story.reply_cached_media
            Story.reply_media_group
            Story.reply_photo
            Story.reply_sticker
            Story.reply_video
            Story.reply_video_note
            Story.reply_voice
        """,
        gift="""
        Gift
            Gift.buy
            Gift.send
            Gift.transfer
            Gift.upgrade
            Gift.convert
            Gift.hide
            Gift.show
            Gift.link
            Gift.wear
            Gift.owned_gift_id
            Gift.send_purchase_offer
            Gift.get_auction_state
        """,
        poll="""
        Poll
            Poll.get_vote_percentage
        """,
        pre_checkout_query="""
        PreCheckoutQuery
            PreCheckoutQuery.answer
        """,
        shipping_query="""
        ShippingQuery
            ShippingQuery.answer
        """,
        folder="""
        Folder
            Folder.create_invite_link
            Folder.delete
            Folder.edit
            Folder.exclude_chat
            Folder.include_chat
            Folder.pin_chat
            Folder.remove_chat
            Folder.update_color
        """,
    )

    root = PYROGRAM_API_DEST

    shutil.rmtree(os.path.join(root, "bound-methods"), ignore_errors=True)
    os.makedirs(os.path.join(root, "bound-methods"), exist_ok=True)

    with open(os.path.join(HOME, "template/bound-methods.rst")) as f:
        template = f.read()

    with open(os.path.join(root, "bound-methods/index.rst"), "w") as f:
        fmt_keys = {}

        for k, v in categories.items():
            name, *bound_methods = get_title_list(v)

            fmt_keys.update(
                {
                    f"{k}_hlist": "\n    ".join(
                        "- :{}:`~{}`".format("attr" if is_property(bm) else "meth", bm)
                        for bm in bound_methods
                    )
                }
            )

            fmt_keys.update(
                {
                    f"{k}_toctree": "\n    ".join(
                        "{} <{}>".format(bm.split(".")[1], bm) for bm in bound_methods
                    )
                }
            )

            # noinspection PyShadowingBuiltins
            for bm in bound_methods:
                with open(os.path.join(root, f"bound-methods/{bm}.rst"), "w") as f2:
                    if is_property(bm):
                        title, directive, suffix = bm, "autoattribute", ""
                    else:
                        title, directive, suffix = f"{bm}()", "automethod", "()"

                    f2.write(title + "\n" + "=" * len(title) + "\n\n")
                    f2.write(f".. {directive}:: pyrogram.types.{bm}{suffix}")

        f.write(template.format(**fmt_keys))


def start():
    global page_template
    global toctree

    shutil.rmtree(DESTINATION, ignore_errors=True)

    with open(os.path.join(HOME, "template/page.txt"), encoding="utf-8") as f:
        page_template = f.read()

    with open(os.path.join(HOME, "template/toctree.txt"), encoding="utf-8") as f:
        toctree = f.read()

    generate(TYPES_PATH, TYPES_BASE)
    generate(FUNCTIONS_PATH, FUNCTIONS_BASE)
    generate(BASE_PATH, BASE_BASE)
    pyrogram_api()


if "__main__" == __name__:
    start()
