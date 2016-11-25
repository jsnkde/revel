var Controller = Backbone.Router.extend({
	routes: {
		"": "login",
		"items": "items",
	},

	login: function(){
		if(lview != null){
			lview.render();
		}
	},

	items: function(){
		if(iview != null){
			iview.render();
		}
	}
});

var controller = new Controller();

Backbone.history.start();
