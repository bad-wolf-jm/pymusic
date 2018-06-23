// var itemArray = [
//     { title: "Marvelous Mint", text: "Gelato", picture: "/images/fruits/60Mint.png" },
//     { title: "Succulent Strawberry", text: "Sorbet", picture: "/images/fruits/60Strawberry.png" },
//     { title: "Banana Blast", text: "Low-fat frozen yogurt", picture: "/images/fruits/60Banana.png" },
//     { title: "Lavish Lemon Ice", text: "Sorbet", picture: "/images/fruits/60Lemon.png" },
//     { title: "Creamy Orange", text: "Sorbet", picture: "/images/fruits/60Orange.png" },
//     { title: "Very Vanilla", text: "Ice Cream", picture: "/images/fruits/60Vanilla.png" },
//     { title: "Banana Blast", text: "Low-fat frozen yogurt", picture: "/images/fruits/60Banana.png" },
//     { title: "Lavish Lemon Ice", text: "Sorbet", picture: "/images/fruits/60Lemon.png" }
// ];

// var items = [];

// // Generate 16 items
// for (var i = 0; i < 2; i++) {
// itemArray.forEach(function (item) {
//     items.push(item);
// });
// }


// WinJS.Namespace.define("Sample.ListView", {
// modes: {
//     readonly: {
//         name: 'readonly',
//         selectionMode: WinJS.UI.SelectionMode.none,
//         tapBehavior: WinJS.UI.TapBehavior.none
//     },
//     single: {
//         name: 'single',
//         selectionMode: WinJS.UI.SelectionMode.single,
//         tapBehavior: WinJS.UI.TapBehavior.directSelect
//     },
//     extended: {
//         name: 'extended',
//         selectionMode: WinJS.UI.SelectionMode.multi,
//         tapBehavior: WinJS.UI.TapBehavior.directSelect
//     },
//     multi: {
//         name: 'multi',
//         selectionMode: WinJS.UI.SelectionMode.multi,
//         tapBehavior: WinJS.UI.TapBehavior.toggleSelect
//     }
// },
// listView: null,
// changeSelectionMode: WinJS.UI.eventHandler(function (ev) {
//     var listView = Sample.ListView.listView;
//     if (listView) {
//         var command = ev.target;
//         if (command.textContent) {
//             var mode = command.textContent.toLowerCase();
//             listView.selection.clear();

//             Sample.ListView.context.currentMode = Sample.ListView.modes[mode];

//             listView.selectionMode = Sample.ListView.context.currentMode.selectionMode;
//             listView.tapBehavior = Sample.ListView.context.currentMode.tapBehavior;
//         }
//     }
// }),
// data: new WinJS.Binding.List(items),
// context: {
// }
// });

// Sample.ListView.context = WinJS.Binding.as({ currentMode: Sample.ListView.modes.readonly });
// var header = document.querySelector('.headerFooterPlaceholder');
// WinJS.Binding.processAll(header, Sample.ListView).then(function () {
// return WinJS.UI.processAll();
// }).then(function () {
// Sample.ListView.listView = document.querySelector('.listView').winControl;
// });

WinJS.Application.onready = function () {

    // The next line will apply declarative control binding to all elements
    // (e.g. DIV with attribute: data-win-control="WinJS.UI.Rating")
    WinJS.UI.processAll();
};

WinJS.Application.start();


