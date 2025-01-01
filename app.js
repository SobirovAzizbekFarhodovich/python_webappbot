let tg = window.Telegram.WebApp;

tg.expand();

tg.MainButton.textColor = '#FFFFF';
tg.MainButton.color = '#2cab37'

let items = [];

function toggleItem(btn, itemId, price) {
    let item = items.find(i => i.id ===itemId);
    if (item) {
        let newItem = {id:itemId, price:price};
        items.push(newItem);
        btn.classList.add('added-to-cart');
        btn.innerText = "Delete from box";
        let totalPrice = items.reduce((total, item) => total + item.price, 0);
        if (totalPrice > 0) {
            tg.MainButton.setText('Total price: ${totalPrice}');
            if (!tg.MainButton.isVisible) {
                tg.MainButton.show();
            }
        } else {
            tg.MainButton.hide();
        }
    } else {
        let index = items.indexOf(item);
        items.splice(index,1);
        btn.classList.remove('added-to-cart');
        btn.innerText = "Add to box";
        let totalPrice = items.reduce((total,item) => total + item.price, 0);
        if (totalPrice > 0) {
            tg.MainButton.setText('Total price: ${totalPrice}');
            if (!tg.MainButton.isVisible) {
                tg.MainButton.show();
            }
        } else {
            tg.MainButton.hide();
        }
    }
}

Telegram.WebApp.onEvent("mainButtonClicked", function(){
    let data = {
        items:items,
        totalPrice:calculateTotalPrice()
    };
    tg.sendData(JSON.stringify(data));
})

function calculateTotalPrice(){
    return items.reduce((total, item) => total + item.price, 0);
}

document.getElementById("btn1").addEventListener("click", function(){
    toggleItem(this, "item1", 2000);
});