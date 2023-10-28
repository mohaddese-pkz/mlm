from django.urls import path
from .Api_view import *
from . import Api_view

app_name = 'ApiMlm'


urlpatterns = [
    path('usersNationalCods/', NationalCodeLists, name='NationalCodeLists'),
    path('category/', Category_list.as_view(), name='category_api'),
    path('userowner/', userOwner.as_view(), name='userowner_api'),
    path('get_owner/', get_owner_class.as_view(), name='get_owner_api'),
    path('commision/', commision_class.as_view(), name='commision_api'),
    path('identify_pursant/', identify_pursant_class.as_view(), name='identify_pursant_api'),
    path('pursant/', pursant_class.as_view(), name='pursant_api'),
    path('create_category/', category_class.as_view(), name='create_category_api'),
    path('seeBranches/', seeBranches.as_view(), name='seeBranches_api'),
    path('seeBranchesN/', seeBranchesN.as_view(), name='seeBranches_api'),

    ############ wallet needs
    path('requests/', Requests, name='requests_api'),
    path('store/', store, name='store_api'),
    path('pickup/', Pickup, name='pickup_api'),
    # path('settle/', settle, name='settle_api'),
    path('adjust/', adjust, name='adjust_api'),
    path('transmition/', transmition, name='transmition_api'),
    path('SumOfOrders/', SumOfOrders, name='SumOfOrders'),
    path('admin_wallet_change/', admin_wallet_change, name='admin_wallet_change_api'),

    ################# online and personal products
    path('list_online_products/', list_online_products, name='list_online_products_api'),
    path('list_personal_products/', list_personal_products, name='list_personal_products_api'),
    path('listOnlineProductsA/', listOnlineProductsA, name='listOnlineProductsA_api'),
    path('listPersonalProductsA/', listPersonalProductsA, name='listPersonalProductsA_api'),
    path('changeStatusOProductsA/', change_Status_Online_ProductsA, name='changeStatusOnline_api'),
    path('changeStatusPProductsA/', change_Status_Personal_ProductsA, name='changeStatusPersonal_api'),

    ######### SEMINAR
    path('seminarpartcipate/', participateSeminar, name='participateseminar_api'),
    path('seminarList/', listSeminar, name='seminarList_api'),
    path('deleteSeminarA/', deleteSeminarAdmin, name='deleteSeminarA_api'),
    path('addSeminarA/', addSeminarAdmin, name='addSeminarA_api'),
    path('endSeminarA/', seminarEndA, name='addSeminarA_api'),
    path('seminarListA/', seminarListA, name='ListSeminarA_api'),
    path('seminarListA/user/', seminarListUserA, name='ListSeminarUserA_api'),

    ######### copons
    path('copons/', copons, name='copons_api'),
    path('addCoponsA/', addCoponsA, name='addCoponsA_api'),

    ######### KATALOGS
    path('catalogs/', catalogs, name='catalogs_api'),
    path('addCatalogsA/', addCatalogsA, name='addcatalogs_api'),
    path('deletecatalogA/', deleteCatalogsA, name='deleteCatalogs_api'),

    ########## comments
    path('comments/', commentLists, name='comments_api'),
    path('responses/', responseList, name='comments_api'),
    path('addTitleA/', addTitleA, name='addtitle_api'),
    path('seeTitlesIdA/', seeTitlesId, name='seetitle_api'),
    path('addResponseA/', addResponseA, name='response_api'),
    path('deleteCommentA/', deleteCommentA, name='deleteComment_api'),
    path('deleteRespA/', deleteRespA, name='deleteResp_api'),
    path('seeResponseIdA/', seeResponseId, name='seetitle_api'),
    path('paComments/', paComments, name='paComments_api'),
    path('seeResultsA/', seeResultsA, name='seeResultsA_api'),

    ########## consulation
    path('consulation/', reqCons, name='consulation_api'),
    path('consA/', consListA, name='consA_api'),

    ######### tickets
    path('ticketsList/', ticketList, name='ticketList_api'),
    path('sendTitle/', sendTitle, name='sendTitle_api'),
    path('sendMessage/', sendMessage, name='sendMessage_api'),
    path('messageTicket/', messageTicketL, name='messageTicket_api'),
    path('ticketListA/', ticketListA, name='ticketListA_api'),
    path('messageTicketLA/', messageTicketLA, name='messageTicketLA_api'),
    path('sendTitleA/', sendTitleA, name='sendTitleA_api'),
    path('sendTitleAllA/', sendTitleAllA, name='sendTitleA_api'),
    path('sendMessageA/', sendMessageA, name='sendMessageA_api'),

    ########### offers
    path('seeOffers/', seeOffers, name='seeOffers_api'),
    path('addOffers/', addOffers, name='addOffers_api'),
    path('seeOffersA/', seeOffersA, name='seeOffers_api'),


    ########### payment report
    path('paymentReport/', paymentReport, name='paymentReport_api'),

    ########### agency
    path('agencyRequest/', agencyRequest, name='agencyRequest_api'),
    path('agencyListA/', agencyListA, name='agencyListA_api'),
    path('deleteAgencyA/', deleteAgencyA, name='deleteAgencyA_api'),
    path('confirmAgencyA/', confirmAgencyA, name='confirmAgencyA_api'),
    path('confirmAgencyListA/', confirmAgencyListA, name='confirmAgencyListA_api'),
    path('AgencyListA/', AgencyListA, name='confirmAgencyListA_api'),

    ########### enrol again
    path('enrolAgain/', enrolAgain, name='enrolAgain_api'),

    ############### didactic file
    path('didacticFiles/', didacticFiles, name='didacticFiles_api'),
    path('addFilesA/', addFilesA, name='addFilesA_api'),
    path('deleteFilesA/', deleteFilesA, name='deleteFilesA_api'),

    ############## Product comments
    path('addProComment/', addProComment, name='addProComment_api'),
    path('newProCommentA/', newProCommentA, name='newProCommentA_api'),
    path('procommentList/<int:id>', procommentList.as_view(), name='procommentList'),
    path('confirmProCommentA/', confirmProCommentA, name='confirmProCommentA_api'),
    path('rejectProCommentA/', rejectProCommentA, name='rejectProCommentA_api'),
    path('confirmProCommentListA/', confirmProCommentLA, name='confirmProCommentLA_api'),
    path('ProCommentListA/', ProCommentLA, name='confirmProCommentLA_api'),

    ############## Products
    # path('OnlineProductsListA/', OnlineProductsListA, name='OnlineProductsListA_api'),
    path('addOnlineProductA/', addOnlineProductA.as_view(), name='addOnlineProductA_api'),
    path('deleteOnlineProductA/', deleteOnlineProductA, name='deleteOnlineProductA_api'),
    # path('PersonalProductsListA/', PersonalProductsListA, name='PersonalProductsListA'),
    # path('addPersonalProductA/', addPersonalProductA, name='addPersonalProductA'),
    # path('deletePersonalProductA/', deletePersonalProductA, name='deletePersonalProductA'),
    
    ############# beni
    path('user-info/', Api_view.user_info.as_view(), name='user_info'),
    path('profile-update/', Api_view.profile_update.as_view(), name='profile_update'),
    path('orders-list/', Api_view.orders_list.as_view(), name='orders_list'),

    path('carts/carts-add/', Api_view.carts_add.as_view(), name='carts_add'),
    path('carts/carts-remove/', Api_view.carts_remove.as_view(), name='carts_remove'),
    path('carts/carts-list/', Api_view.carts_list.as_view(), name='carts_list'),

    # Api Products
    path('products/products-list/', Api_view.products_list.as_view(), name='products_list'),
    path('products/details/<int:id>/<str:slug>', product_details.as_view(), name='product_details'),
    path('products/products-comments-add/', Api_view.products_comments_add.as_view(), name='products_comments_add'),
    path('products/products-comments-list/<int:id>/', Api_view.products_comments_list.as_view(), name='products_comments_list'),
    path('products/products-filter-maincategory-list/', Api_view.products_filter_maincategory_list.as_view(),name='products_filter_maincategory_list'),

    #product categories
    path('main/category/', MainCat, name='mainCategory'),
    path('sub1/category/<int:id>', SubCat1, name='subCategory1'),
    path('sub2/category/<int:id>', SubCat2, name='subCategory2'),

 ]
