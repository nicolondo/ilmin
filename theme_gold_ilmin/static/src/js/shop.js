odoo.define('ilmin_theme.website_shop', function (require) {
'use strict';
    var publicWidget = require('web.public.widget');
    var ajax = require('web.ajax');
    var wSaleUtils = require('website_sale.utils');

   require("web.dom_ready");


    $(".quick_add_to_cart").unbind().click(function (ev) {
        ev.preventDefault();
        var $aSubmit = $(ev.currentTarget);
        var frm = $aSubmit.closest('ul');
        var parent = $aSubmit.closest('.card-body');
        var $trash = frm.find('.action-trash');
        var product_product = frm.parent().find('input[name="product_id"]').attr("value");
        var product_price = parseFloat(frm.find('.product_variant_price').find(".oe_currency_value").text());
        var $input = frm.find('input[name="add_qty"]')
        var line_id = frm.parent().parent().parent().find('input[name="line_id"]').attr("value");
        var $qtyNavBar = $(".my_cart_qty");
        var $cart_lines_ilmin= $('#cart_lines_ilmin')
        var $cart_sammury_ilmin= $('#cart_sammury_ilmin')

        var $amountNavBar = $(".my_cart_amount");
        var data = {cart_quantity:parseFloat($qtyNavBar.text() || 0),cart_total:parseFloat($amountNavBar.text() || 0)};
        var min = parseFloat($input.data("min") || 0);
        var max = parseFloat($input.data("max") || Infinity);
        var previousQty = parseFloat($input.val() || 0, 2);
        var previousTotal = data.cart_total;
        var $ineTotal = frm.find('.line_total_price')
        var $productTmplineTotal = parent.find('.total_product')

        if($aSubmit.hasClass('add_mass')){
            var add_qty = parseFloat($aSubmit.attr('qty'));
            var quantity =add_qty + previousQty;
            var add_amount =add_qty * product_price;
            var newQty = quantity > min ? (quantity < max ? quantity : max) : min;


            if (newQty !== previousQty & newQty > 0) {


                ajax.jsonRpc('/shop/cart/update_custom', 'call',{'product_id':product_product,'line_id':line_id,'set_qty':newQty}).then(function(result) {
                   $input.val(newQty).trigger('change');
                   $qtyNavBar.text(result.cart_qty);
                   $amountNavBar.html(result.cart_amount_total)
                   $ineTotal.html(result.line_total)
                   $productTmplineTotal.html(result.product_tmlp_total)
                   $input.parent().removeClass('invisible');
                   $trash.removeClass('invisible');
                   $cart_lines_ilmin.html(result.cart_lines_ilmin);
                   $cart_sammury_ilmin.html(result.cart_sammury_ilmin);


                });
            }else{

                ajax.jsonRpc('/shop/cart/update_custom', 'call',{'product_id':product_product,'line_id':line_id,'set_qty':0}).then(function(result) {
                   $input.val(0).trigger('change');
                   $qtyNavBar.text(result.cart_qty);
                   $amountNavBar.html(result.cart_amount_total)
                   $ineTotal.html(result.line_total)
                   $productTmplineTotal.html(result.product_tmlp_total)

                   $input.parent().addClass('invisible');
                    $trash.addClass('invisible');
                   $cart_lines_ilmin.html(result.cart_lines_ilmin);
                   $cart_sammury_ilmin.html(result.cart_sammury_ilmin);

                });

            }

        }else if ($aSubmit.hasClass('js_add_cart_json_ilmin')) {
            var add_or_remove_qty = ($aSubmit.has(".fa-minus").length ? -1 : 1);
            var add_amount =add_or_remove_qty * product_price;
            var quantity =  add_or_remove_qty+ previousQty;
            var newQty = quantity > min ? (quantity < max ? quantity : max) : min;
            data.cart_quantity = data.cart_quantity + add_or_remove_qty


            if (newQty !== previousQty & newQty > 0) {


                ajax.jsonRpc('/shop/cart/update_custom', 'call',{'product_id':product_product,'line_id':line_id,'set_qty':newQty}).then(function(result) {
                   $input.val(newQty).trigger('change');
                   $qtyNavBar.text(result.cart_qty);
                   $amountNavBar.html(result.cart_amount_total)
                                      $ineTotal.html(result.line_total)
                   $productTmplineTotal.html(result.product_tmlp_total)

                   $input.parent().removeClass('invisible');
                    $trash.removeClass('invisible');
                   $cart_lines_ilmin.html(result.cart_lines_ilmin);
                   $cart_sammury_ilmin.html(result.cart_sammury_ilmin);

                });
            }else{

                ajax.jsonRpc('/shop/cart/update_custom', 'call',{'product_id':product_product,'line_id':line_id,'set_qty':0}).then(function(result) {
                   $input.val(0).trigger('change');
                   $qtyNavBar.text(result.cart_qty);
                   $amountNavBar.html(result.cart_amount_total)
                                      $ineTotal.html(result.line_total)
                   $productTmplineTotal.html(result.product_tmlp_total)

                   $input.parent().addClass('invisible');
                   $trash.addClass('invisible');
                   $cart_lines_ilmin.html(result.cart_lines_ilmin);
                   $cart_sammury_ilmin.html(result.cart_sammury_ilmin);

                });

            }

        }else if ($aSubmit.hasClass('js_delete_product_ilmin')) {
            var newQty = 0

            if (newQty !== previousQty) {


                ajax.jsonRpc('/shop/cart/update_custom', 'call',{'product_id':product_product,'line_id':line_id,'set_qty':0}).then(function(result) {
                   $input.val(newQty).trigger('change');
                   $qtyNavBar.text(result.cart_qty);
                   $amountNavBar.html(result.cart_amount_total)
                   $input.parent().addClass('invisible');
                   $trash.addClass('invisible');
                   $ineTotal.html(result.line_total)
                   $productTmplineTotal.html(result.product_tmlp_total)
                   $cart_lines_ilmin.html(result.cart_lines_ilmin);
                   $cart_sammury_ilmin.html(result.cart_sammury_ilmin);


                });


            }
        }




    });

    $(".my_cart_icon").click(function (ev) {
        $(".cart_ilmin").toggle('slow')
    })
    $(".my_cart_qty").click(function (ev) {
        $(".cart_ilmin").toggle('slow')
    })
    $(".my_cart_amount").click(function (ev) {
        $(".cart_ilmin").toggle('slow')
    })
    $(".my_cart_items").click(function (ev) {
        $(".cart_ilmin").toggle('slow')
    })


     $(document).on('click',function(e){
        if(!(($(e.target).closest("#modalBox").length > 0 ) || ($(e.target).closest("#modal-btn").length > 0))){
        $("#modalBox").hide();
       }
      })
    $("#all_adress_shipping").on("click", "input[name='pickadresse']", function(ev){
         var $old = $('.shippement_selected');
        $old.removeClass('shippement_selected');

        var $new = $(ev.currentTarget).closest('.card');
        $new.addClass('shippement_selected');
        var new_street = $new.find("address").find('span.w-100').html()
        var regex = /<br\s*[\/]?>/gi;
        $("#selected_adress_value").html('<span class="w-100 o_force_ltr d-block" itemprop="streetAddress">'.concat(new_street).concat('</span>'))



        $("#address_on_payment").toggle('show')
        $("#cart_lines_ilmin").toggle('show')




    })
    $("#cart_sammury_ilmin").on("click", "#choose_address", function(ev){
        $("#address_on_payment").toggle('show')
        $("#cart_lines_ilmin").toggle('show')

    })

    $("#all_adress_shipping").on("click", "#add_adress", function(ev){
        $('#form_add_adress')[0].reset()
        $("#ilmin_add_edit_adress").toggle('show')

    })

    $("#clear_search").click(function (ev) {
         $(".oe_search_box").val('')
         $(".o_searchbar_form").submit()
    })

    $("body").mouseup(function(e){
        var container = $(".cart_ilmin");

        // If the target of the click isn't the container
        if(!container.is(e.target) && container.has(e.target).length === 0){
            container.hide();
        }
    });

    $("#ilmin_add_edit_adress").on("click", "#add_edit_adress_btn", function(ev){
        var unindexed_array  = $('#form_add_adress').serializeArray();
        var formData = {};

            $.map(unindexed_array, function(n, i){
                formData[n['name']] = n['value'];
            });

        ajax.jsonRpc('/shop/cart/create_contacts', 'call',{'data':formData}).then(function(data) {
           if(data){

               $("#ilmin_add_edit_adress").toggle('show')
                $("#all_adress_shipping").html(data.all_adress_shipping)


           }
        });


    })
    $("#all_adress_shipping").on("click", ".edit_address", function(ev){
        ajax.jsonRpc('/shop/cart/getcontact_info', 'call',{'contact_id':$(this).attr("data-contact-id")}).then(function(data) {
           if(data){
               $.each(data, function(key, value){
                    if(value){
                        $("#form_add_adress").find('input[name='+key+']').val(value)
                    }else{
                        $("#form_add_adress").find('input[name='+key+']').val(" ")
                    }
                });
                $("#ilmin_add_edit_adress").toggle('show')
            }
        });
    })

    $("#cart_sammury_ilmin").on("click", "#finalise-btn", function(ev){
        var proceed = confirm('CONFIRMACION Estas a punto de confirmar tu orden, éste paso no tiene vuelta atrás !');
            if(proceed)  {
            var contact_id = $('.shippement_selected').find('.edit_address').attr("data-contact-id");
            ajax.jsonRpc('/shop/cart/shop_confirm_order', 'call',{'contact_id':contact_id}).then(function(data) {
               if(data['success']){
                    var alert = $('#alert_order_success')
                    alert.find('#order_alert').text(data['order_name']);
                    alert.toggle('show')

                    window.location.replace(data['url'])
              }else{
                    var alert = $('#alert_order_failed')
                    alert.toggle('show')
              }
            });
        }
    })



});
