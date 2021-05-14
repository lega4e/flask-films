
window.switch_search = function()
{
	switcher = $('#search-switcher');
	text     = $('#search');

	if(text.attr('hidden'))
	{
		text.attr('hidden', false);
		switcher.val('Скрыть параметры поиска');
	}
	else
	{
		text.attr('hidden', true)
		switcher.val('Показать параметры поиска');
	}
}

