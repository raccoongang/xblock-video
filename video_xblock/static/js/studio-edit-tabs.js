/**
    Create basic and advanced tabs for studio editor.
*/
domReady(function() {
    var $modalHeaderTabs = $('.editor-modes.action-list.action-modes');
    var currentTabName;

    /** Toggle studio editor's current tab.
     */
    function toggleEditorTab(currentTabName) {
        'use strict';
        var tabDisable;
        var tabEnable;
        var otherTabName;
        if (currentTabName === 'Basic') {
            tabEnable = $('.list-input.settings-list.basic');
            tabDisable = $('.list-input.settings-list.advanced');
            otherTabName = 'Advanced';
        } else if (currentTabName === 'Advanced') {
            tabEnable = $('.list-input.settings-list.advanced');
            tabDisable = $('.list-input.settings-list.basic');
            otherTabName = 'Basic';
        }
        $(event.currentTarget).addClass('current');
        $('.tab[data-tab-name=' + otherTabName + ']').removeClass('current');
        tabDisable.addClass('is-hidden');
        tabEnable.removeClass('is-hidden');
    }

    // Create advanced and basic tabs
    (function() {
        $modalHeaderTabs
            .append(
                '<li class="inner_tab_wrap"><button class="tab" data-tab-name="Advanced">Advanced</button></li>',
                '<li class="inner_tab_wrap"><button class="tab current" data-tab-name="Basic">Basic</button></li>');
        // Bind listeners to the buttons
        $('.tab').click(function(event) {
            currentTabName = $(event.currentTarget).attr('data-tab-name');
            toggleEditorTab(currentTabName);
            // if (currentTab === 'Basic') {
            //     $(event.currentTarget).addClass('current');
            //     $('.tab[data-tab-name="Advanced"]').removeClass('current');
            //     $('.list-input.settings-list.advanced').addClass('is-hidden');
            //     $('.list-input.settings-list.basic').removeClass('is-hidden');
            // } else if (currentTab === 'Advanced') {
            //     $(event.currentTarget).addClass('current');
            //     $('.tab[data-tab-name="Basic"]').removeClass('current');
            //     $('.list-input.settings-list.basic').addClass('is-hidden');
            //     $('.list-input.settings-list.advanced').removeClass('is-hidden');
            // }
        });
    }());
});
