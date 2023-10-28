import datetime

from django.db import models
from Users.models import Users
from extensions.DateJalali import django_jalali
from extensions.optimization import photo_optimization


class UserOwner(models.Model):

    MlmOwner = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='userOwner', null=True, blank=True)
    MlmUser = models.ForeignKey(Users, on_delete=models.CASCADE, null=True, blank=True)


class Category(models.Model):

    OwnerCategory = models.CharField(max_length=90, verbose_name='ownercategory')
    points = models.IntegerField(null=True, blank=True, verbose_name='points')
    Id = models.ForeignKey(Users, on_delete=models.CASCADE, null=True, blank=True)


class IsMoshaver(models.Model):

    user = models.ForeignKey(Users, on_delete=models.CASCADE, verbose_name='user')
    flag = models.IntegerField(verbose_name='flag')


class Pursant(models.Model):

    user = models.ForeignKey(Users, on_delete=models.CASCADE, verbose_name='user')
    amount = models.IntegerField(verbose_name='amount')
    reson = models.CharField(max_length=999, verbose_name='reson')
    date = models.DateTimeField(auto_now_add=True, verbose_name='date')
    status = models.BooleanField(default=False, verbose_name='status')


class GivePursant(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, name='user')
    date = models.DateField(default=datetime.date.today(), verbose_name='date')
    reson = models.CharField(max_length=999, verbose_name='reson')



class UserWalletRequest(models.Model):

    user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True, blank=True)
    store = models.IntegerField(verbose_name='store', default=0)
    requests = models.IntegerField(verbose_name='requests')
    type = models.CharField(max_length=999, verbose_name='type', null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, verbose_name='date')
    status = models.BooleanField(default=False, verbose_name='status')


class Seminars(models.Model):
    name = models.CharField(max_length=999, verbose_name='name')
    description = models.CharField(max_length=999, verbose_name='description')
    image = models.ImageField(upload_to='seminarpic', verbose_name='image')
    date = models.DateTimeField(verbose_name='date')
    status = models.BooleanField(default=False, verbose_name='status')


class ParticipatSeminar(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, verbose_name='user')
    info = models.ForeignKey(Seminars, on_delete=models.CASCADE, verbose_name='info')


class Copons(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, verbose_name='user')
    name = models.CharField(max_length=999, verbose_name='name')
    percentage = models.IntegerField(verbose_name='percentage')






class MlmProductSubCategories_2(models.Model):
    name = models.CharField(max_length=999, verbose_name='Name')

    def __str__(self):
        return f'{self.name}'


class MlmProductSubCategories_1(models.Model):
    name = models.CharField(max_length=999, verbose_name='Name')
    sub_categories2 = models.ManyToManyField(MlmProductSubCategories_2, blank=True, verbose_name='Sub Categories 2')

    def __str__(self):
        return f'{self.name}'


class MlmProductMainCategories(models.Model):
    name = models.CharField(max_length=999, verbose_name='Name')
    image = models.ImageField(upload_to='ProductMainCategoriesImage', blank=True, null=True, verbose_name='Image')
    sub_categories1 = models.ManyToManyField(MlmProductSubCategories_1, blank=True, verbose_name='Sub Categories 1')

    def save(self, *args, **kwargs):
        photo_optimization(self.image)
        super(MlmProductMainCategories, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}'

class MlmProducts(models.Model):
    user = models.ForeignKey(Users,on_delete=models.CASCADE,blank=True,null=True,verbose_name='USer')
    title = models.CharField(max_length=999,verbose_name='Title')
    slug = models.CharField(max_length=999,verbose_name='Slug')
    descriptions = models.CharField(max_length=999,verbose_name='Descriptions')
    image = models.ImageField(upload_to='Products',verbose_name='Image')
    image1 = models.ImageField(upload_to='Products',blank=True,null=True,verbose_name='Image1')
    image2 = models.ImageField(upload_to='Products',blank=True,null=True,verbose_name='Image2')
    image3 = models.ImageField(upload_to='Products',blank=True,null=True,verbose_name='Image3')
    price = models.IntegerField(default=0)
    maincategories = models.ManyToManyField(MlmProductMainCategories,blank=False,verbose_name='Main Category')
    subCategories1 = models.ManyToManyField(MlmProductSubCategories_1,blank=False,verbose_name='Sub Category 1')
    subCategories2 = models.ManyToManyField(MlmProductSubCategories_2,blank=False,verbose_name='Sub Category 2')
    volume = models.CharField(max_length=999, verbose_name='Volume')
    compounds = models.CharField(max_length=999, verbose_name='Compounds')
    licenseـissuer = models.CharField(max_length=999, verbose_name='License issuer')
    date = models.DateTimeField(auto_now_add=True)
    limit = models.IntegerField(default=0,blank=False,null=False,verbose_name='Limit')
    score = models.FloatField(default=1, verbose_name='score')
    status = models.BooleanField(default=True)

    def jdate(self):
        return django_jalali(self.date)

    def save(self, *args, **kwargs):
        photo_optimization(self.image)
        photo_optimization(self.image1)
        photo_optimization(self.image2)
        photo_optimization(self.image3)
        super(MlmProducts, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

class MlmProductsComments(models.Model):
    user = models.ForeignKey(Users,null=False, blank=False,on_delete=models.CASCADE,verbose_name='User')
    product = models.ForeignKey(MlmProducts,null=False, blank=False, on_delete=models.CASCADE,verbose_name='Prodcut Id')
    comment = models.TextField(null=False, blank=False,verbose_name='Comment')
    status = models.BooleanField(default=False, verbose_name='Status')
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='Date')

    def user_fullname(self):
        return f'{self.user.first_name} {self.user.last_name}'

    def jdate(self):
        return django_jalali(self.date)

    def __str__(self):
        return self.comment

class MlmProductsSliders(models.Model):
    image = models.ImageField(upload_to='ProductsSlides',verbose_name='Image')
    url = models.URLField(verbose_name='Url')

    def save(self, *args, **kwargs):
        photo_optimization(self.image)
        super(MlmProductsSliders, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.url}"





class MlmProductsCarts(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, verbose_name='Shoper')
    payment_date = models.DateTimeField(auto_now_add=True,blank=True,null=True, verbose_name='Payment Date')
    payment_status = models.BooleanField(default=False, verbose_name='Payment Status')

    def jdate(self):
        return django_jalali(self.payment_date)

    def __str__(self):
        return f'{self.user}'


class MlmProductsOrders(models.Model):
    cart = models.ForeignKey(MlmProductsCarts, on_delete=models.CASCADE,blank=True, null=True,verbose_name='Cart')
    shopper = models.ForeignKey(Users, on_delete=models.CASCADE, blank=True, null=True, verbose_name='shopper')
    title = models.CharField(blank=True, null=True, max_length=999, verbose_name='Title')
    description = models.TextField(blank=True, null=True, verbose_name='Description')
    count = models.IntegerField(blank=True, null=True, verbose_name='count')
    price = models.IntegerField(blank=True, null=True, verbose_name='Price')
    product = models.ForeignKey(MlmProducts, on_delete=models.CASCADE, blank=False, null=False, verbose_name='Product')
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name='Payment Date')
    payment_status = models.BooleanField(default=False, verbose_name='Payment Status')

    def product_image(self):
        if self.product.image.url:
            return self.product.image.url
        else:
            return None

    def user_address(self):
        return self.shopper.address

    def jdate(self):
        return django_jalali(self.payment_date)

    def __str__(self):
        return f'{self.title}'



class MlmTiket(models.Model):
    title = models.CharField(max_length=999,verbose_name='Title')
    user = models.ForeignKey(Users,on_delete=models.CASCADE,null=True,blank=True,verbose_name='User',related_name='usertiketmlm')
    support = models.ForeignKey(Users,on_delete=models.CASCADE,null=False,blank=False,verbose_name='Support',related_name='supporttiketmlm')
    status = models.BooleanField(default=False,verbose_name='Status')
    date = models.DateTimeField(auto_now_add=True,verbose_name='Date')

    def jdate(self):
        return django_jalali(self.date)



class MlmMessages(models.Model):
    tiket = models.ForeignKey(MlmTiket,on_delete=models.CASCADE,verbose_name='Tiket')
    user = models.ForeignKey(Users,on_delete=models.CASCADE,verbose_name='User',related_name='mlmUser')
    support = models.ForeignKey(Users,on_delete=models.CASCADE,null=True,blank=True,verbose_name='Support',related_name='supportmlm')
    text = models.TextField(null=True,blank=True,verbose_name='Text')
    file = models.FileField(upload_to='TiketFile',blank=True,null=True,verbose_name='File')
    date = models.DateTimeField(auto_now_add=True,verbose_name='Date')
    is_support = models.BooleanField(default=False,verbose_name='Is Support')

    def jdate(self):
        return django_jalali(self.date)

    def status(self):
        if self.tiket.status:
            return self.tiket.status
        else:
            return None

class DiscountCode(models.Model):
    user = models.ForeignKey(Users,on_delete=models.CASCADE,verbose_name='User')
    code = models.CharField(max_length=999,verbose_name='Code')
    status = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.code}'
        
        

class MlmProductsPersonal(models.Model):
    user = models.ForeignKey(Users,on_delete=models.CASCADE,blank=True,null=True,verbose_name='USer')
    title = models.CharField(max_length=999, verbose_name='Title')
    slug = models.CharField(max_length=999, verbose_name='Slug')
    descriptions = models.CharField(max_length=999,verbose_name='Descriptions')
    image = models.ImageField(upload_to='Products',verbose_name='Image')
    image1 = models.ImageField(upload_to='Products',blank=True,null=True,verbose_name='Image1')
    image2 = models.ImageField(upload_to='Products',blank=True,null=True,verbose_name='Image2')
    image3 = models.ImageField(upload_to='Products',blank=True,null=True,verbose_name='Image3')
    price = models.IntegerField(default=0)
    maincategories = models.ManyToManyField(MlmProductMainCategories,blank=False,verbose_name='Main Category')
    subCategories1 = models.ManyToManyField(MlmProductSubCategories_1,blank=False,verbose_name='Sub Category 1')
    subCategories2 = models.ManyToManyField(MlmProductSubCategories_2,blank=False,verbose_name='Sub Category 2')
    volume = models.CharField(max_length=999,verbose_name='Volume')
    compounds = models.CharField(max_length=999,verbose_name='Compounds')
    licenseـissuer = models.CharField(max_length=999,verbose_name='License issuer')
    date = models.DateTimeField(auto_now_add=True)
    limit = models.IntegerField(default=0,blank=False,null=False,verbose_name='Limit')
    status = models.BooleanField(default=True)

    def jdate(self):
        return django_jalali(self.date)

    def save(self, *args, **kwargs):
        photo_optimization(self.image)
        photo_optimization(self.image1)
        photo_optimization(self.image2)
        photo_optimization(self.image3)
        super(MlmProducts, self).save(*args, **kwargs)

    def __str__(self):
        return self.title







class Catalogs(models.Model):
    title = models.TextField(verbose_name='title')
    file = models.FileField(upload_to='catalogs', verbose_name='file')



class ResponseC(models.Model):
    response = models.TextField(verbose_name='response')
    numbers = models.IntegerField(verbose_name='numbers')
    IdT = models.IntegerField(verbose_name='Id')


class Comments(models.Model):
    title = models.TextField(verbose_name='title')

class CommentsPa(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, verbose_name='user')
    comment = models.ForeignKey(Comments, on_delete=models.CASCADE, verbose_name='comment')



class Consultation(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, verbose_name='user')
    product = models.ForeignKey(MlmProducts, on_delete=models.CASCADE, verbose_name='product')



class Ticket(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, verbose_name='user')
    title = models.TextField(verbose_name='title')
    IsAdmin = models.BooleanField(default=False, verbose_name='IsAdmin', blank=True, null=True)



class TicketMessage(models.Model):
    messages = models.TextField(verbose_name='messages')
    file = models.FileField(upload_to='ticketFile', verbose_name='file', blank=True, null=True)
    IdT = models.CharField(max_length=9999, verbose_name='Id')



class Offers(models.Model):

    user = models.ForeignKey(Users, on_delete=models.CASCADE, verbose_name='user')
    text = models.TextField(verbose_name='text')




class Agency(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, verbose_name='user')
    status = models.BooleanField(default=False, verbose_name='status')

class DidacticFile(models.Model):
    title = models.CharField(max_length=999, verbose_name='title')
    files = models.FileField(upload_to='didacticFile', verbose_name='files')

class ProductComment(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, verbose_name='user')
    product = models.ForeignKey(MlmProducts, on_delete=models.CASCADE, verbose_name='product')
    comment = models.TextField(verbose_name='comment')
    status = models.CharField(max_length=999, choices=[('not seen', 'not seen'), ('confirm', 'confirm'), ('reject', 'reject')], default='not seen')













