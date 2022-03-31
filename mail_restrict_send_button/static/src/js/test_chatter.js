odoo.define("mail_restrict_send_button.restrict_send_buttons", function (require) {
    "use strict";
    
    console.log('Début fonction')
    const { OnChange } = require ("@mail/model/model_onchange");
    const container = require("@mail/components/chatter_container/chatter_container");
    const Chatter = require("@mail/components/chatter/chatter")
    const {registry} = require("@mail/model/model_core");
    const rpc = require("web.rpc");
    const {attr, many2one, one2one} = require("@mail/model/model_field");
    const {clear} = require("@mail/model/model_field_command");
    
    console.log(chatter)
        Chatter.fields = {
            /**
             * Determines the attachment list that will be used to display the attachments.
             */
            attachmentList: one2one('mail.attachment_list', {
                compute: '_computeAttachmentList',
                inverse: 'chatter',
                isCausal: true,
                readonly: true,
            }),
            /**
             * States the OWL component of this chatter top bar.
             */
            componentChatterTopbar: attr(),
            /**
             * Determines the composer view used to post in this chatter (if any).
             */
            composerView: one2one('mail.composer_view', {
                inverse: 'chatter',
                isCausal: true,
            }),
            context: attr({
                default: {},
            }),
            /**
             * Determines whether `this` should display an activity box.
             */
            hasActivities: attr({
                default: true,
            }),
            hasExternalBorder: attr({
                default: true,
            }),
            /**
             * Determines whether `this` should display followers menu.
             */
            hasFollowers: attr({
                default: true,
            }),
            /**
             * Determines whether `this` should display a message list.
             */
            hasMessageList: attr({
                default: true,
            }),
            /**
             * Whether the message list should manage its scroll.
             * In particular, when the chatter is on the form view's side,
             * then the scroll is managed by the message list.
             * Also, the message list shoud not manage the scroll if it shares it
             * with the rest of the page.
             */
            hasMessageListScrollAdjust: attr({
                default: false,
            }),
            /**
             * Determines whether `this.thread` should be displayed.
             */
            hasThreadView: attr({
                compute: '_computeHasThreadView',
            }),
            hasTopbarCloseButton: attr({
                default: false,
            }),
            /**
             * States the id of this chatter. This id does not correspond to any
             * specific value, it is just a unique identifier given by the creator
             * of this record.
             */
            id: attr({
                readonly: true,
                required: true,
            }),
            isActivityBoxVisible: attr({
                default: true,
            }),
            /**
             * Determiners whether the attachment box is currently visible.
             */
            isAttachmentBoxVisible: attr({
                default: false,
            }),
            /**
             * Determiners whether the attachment box is visible initially.
             */
            isAttachmentBoxVisibleInitially: attr({
                default: false,
            }),

            /* ############################################################### */
            /* ############################################################### */
            /* ################Ajout du champs isSendMessage MT############### */
            /* ############################################################### */
            /* ############################################################### */
            isSendMessage: attr({default: true,}),
            /* ############################################################### */
            /* ############################################################### */
            /* ############################################################### */
            /* ############################################################### */
            /* ############################################################### */
            isDisabled: attr({
                compute: '_computeIsDisabled',
                default: false,
            }),
            isShowingAttachmentsLoading: attr({
                default: false,
            }),
            /**
             * Determines the `mail.thread` that should be displayed by `this`.
             */
            thread: many2one('mail.thread'),
            /**
             * Determines the id of the thread that will be displayed by `this`.
             */
            threadId: attr(),
            /**
             * Determines the model of the thread that will be displayed by `this`.
             */
            threadModel: attr(),
            /**
             * States the OWL ref of the "thread" (ThreadView) of this chatter.
             */
            threadRef: attr(),
            /**
             * States the `mail.thread_view` displaying `this.thread`.
             */
            threadView: one2one('mail.thread_view', {
                related: 'threadViewer.threadView',
            }),
            /**
             * Determines the `mail.thread_viewer` managing the display of `this.thread`.
             */
            threadViewer: one2one('mail.thread_viewer', {
                compute: '_computeThreadViewer',
                inverse: 'chatter',
                isCausal: true,
                readonly: true,
                required: true,
            }),
        };
    console.log(chatter.isSendMessage);
    /* ############################################################### */
    /* ############################################################### */
    /* ############################################################### */
    /* ############################################################### */
    /* ############################################################### */
    console.log('Before container props');
    console.log(container);
    console.log(container._insertFromProps);
    container._insertFromProps = function (props) {
        console.log('Start');
        const values = Object.assign({}, props);
        console.log(values);
        rpc.query({model: "mail.followers",method: "check_can_send_message",args: [],}).then((result) => {
            console.log('Valeur result -->');
            console.log(result);
            values.isSendMessage = result;
            if (values.threadId === undefined) {
                // eslint-disable-next-line no-undef
                values.threadId = clear();
            }
            if (!this.chatter) {
                this.chatter = this.env.models["mail.chatter"].create(values);
            } else {
                this.chatter.update(values);
            }
        });
    };
    console.log(container._insertFromProps);
    /* ############################################################### */
    /* ############################################################### */
    /* ############################################################### */
    /* ############################################################### */
    /* ############################################################### */
});
