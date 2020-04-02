import graphene
import hashlib
from graphene_django.types import DjangoObjectType
from api.models import Page, Confession
from django.db.models import F
# Create a GraphQL type for the Page model
class PageType(DjangoObjectType):
    class Meta:
        model = Page
        exclude=('pin',)
    totalConfessions = graphene.Int()

class CreatePageType(DjangoObjectType):
    class Meta:
        model = Page
    totalConfessions = graphene.Int()

# Create a GraphQL type for the Confession model
class ConfessionType(DjangoObjectType):
    class Meta:
        model = Confession
    dateAddedText = graphene.String()

class LoginType(graphene.ObjectType):
    result=graphene.String()


#Query for both Objects
class Query(object):
    #Query with agrs (mainly pageId and confId)
    page = graphene.Field(PageType, pageId=graphene.String()) 
    confessions = graphene.List(ConfessionType, pageId=graphene.String(), confId=graphene.String())
    login = graphene.Field(LoginType,pageId=graphene.String(), loginPin=graphene.String(), auth=graphene.String())
    adminPage = graphene.Field(PageType, pageId=graphene.String(), auth=graphene.String())
    adminConfessions = graphene.List(ConfessionType, pageId=graphene.String(), confId=graphene.String(), auth=graphene.String())

    #resolvers
    def resolve_page(self, info, **kwargs):
        pageId = kwargs.get('pageId')
        return Page.objects.get(pageId=pageId)

    def resolve_confessions(self, info, **kwargs):
        pageId = kwargs.get('pageId')
        confId = kwargs.get('confId')
        if confId:
            if Page.objects.get(pageId=pageId).isPublic:
                return Confession.objects.filter(page__pageId=pageId, confId =confId).order_by('-dateAdded')
            else:
                return None
        else:
            if Page.objects.get(pageId=pageId).isPublic:
                return Confession.objects.filter(page__pageId=pageId).order_by('-dateAdded')
            else:
                return None

    def resolve_login(self, info, **kwargs):
        pageId = kwargs.get('pageId')
        loginPin = kwargs.get('loginPin')
        auth =kwargs.get('auth')
        if loginPin:
            page = Page.objects.get(pageId=pageId) 
            if str(page.pin) == str(loginPin):
                result=hashlib.sha256(loginPin.encode('utf-8')).hexdigest()
                return LoginType(result=result)
            else:
                return LoginType(result=None)
        if auth:
            page = Page.objects.get(pageId=pageId)
            pin=hashlib.sha256(str(page.pin).encode('utf-8')).hexdigest()
            if auth==pin:
                return LoginType(result='success')


    def resolve_adminPage(self, info, **kwargs):
        pageId = kwargs.get('pageId')
        auth =kwargs.get('auth')
        page = Page.objects.get(pageId=pageId)
        pin=hashlib.sha256(str(page.pin).encode('utf-8')).hexdigest()
        if auth==pin:
            return Page.objects.get(pageId=pageId)
    
    def resolve_adminConfessions(self,info, **kwargs):
        pageId = kwargs.get('pageId')
        confId = kwargs.get('confId')
        auth=kwargs.get('auth')
        page = Page.objects.get(pageId=pageId)
        pin=hashlib.sha256(str(page.pin).encode('utf-8')).hexdigest()
        if auth==pin:
            if confId:
                return Confession.objects.filter(page__pageId=pageId, confId =confId).order_by('-dateAdded')
            else:
                return Confession.objects.filter(page__pageId=pageId).order_by('-dateAdded')
                

# MUTATIONS WORK START HERE

# Create Input Object Types
class PageInput(graphene.InputObjectType):
    name = graphene.String()
    isPublic = graphene.Boolean()

class ConfessionInput(graphene.InputObjectType):
    title = graphene.String()
    content = graphene.String()
    pageId = graphene.String()
    
# Create mutations for Page
class CreatePage(graphene.Mutation):
    class Arguments:
        input = PageInput(required=True)

    page = graphene.Field(CreatePageType)

    @staticmethod
    def mutate(root, info, input=None):
        page_instance = Page(name=input.name, isPublic=input.isPublic)
        page_instance.save()
        return CreatePage(page=page_instance)

class DeletePage(graphene.Mutation):
    class Arguments:
        pageId = graphene.String(required=True)
        auth = graphene.String(required=True)

    deleted = graphene.Boolean()

    @staticmethod
    def mutate(root, info, pageId,auth, input=None):
        deleted = False
        page_instance = Page.objects.get(pageId=pageId)
        if page_instance:
            pin=hashlib.sha256(str(page_instance.pin).encode('utf-8')).hexdigest()
            if auth==pin:
                Page.objects.get(pageId=pageId).delete()
                deleted=True
                return DeletePage(deleted=deleted)
        return DeletePage(deleted=deleted)

# Create mutations for Confession
class CreateConfession(graphene.Mutation):
    class Arguments:
        input = ConfessionInput(required=True)

    confession = graphene.Field(ConfessionType)

    @staticmethod
    def mutate(root, info, input=None):
        confession_instance = Confession(title=input.title, content=input.content, page=Page.objects.get(pageId=input.pageId))
        confession_instance.save()
        return CreateConfession(confession=confession_instance)

class DeleteConfession(graphene.Mutation):
    class Arguments:
        pageId = graphene.String(required=True)
        confId = graphene.String(required=True)
        auth=graphene.String(required=True)

    deleted = graphene.Boolean()

    @staticmethod
    def mutate(root, info, confId,auth,pageId, input=None):
        deleted = False
        page_instance = Page.objects.get(pageId=pageId)
        if page_instance:
            pin=hashlib.sha256(str(page_instance.pin).encode('utf-8')).hexdigest()
            if auth==pin:
                confession_instance = Confession.objects.get(confId=confId)
                if confession_instance:
                    Confession.objects.get(confId=confId).delete()
                    deleted=True
                    return DeletePage(deleted=deleted)
        return DeletePage(deleted=deleted)

class LikeConfession(graphene.Mutation):
    class Arguments:
        confId =graphene.String(required=True)
        value = graphene.Int(required=True)

    newLikes = graphene.Int()

    @staticmethod
    def mutate(root, info, confId, value, input=None):
        confession_instance = Confession.objects.get(confId=confId)
        newLikes=confession_instance.likes+value
        confession_instance.likes= newLikes
        confession_instance.save()
        newLikes=Confession.objects.get(confId=confId).likes
        
        return LikeConfession(newLikes=newLikes)

class AdminLikeConfession(graphene.Mutation):
    class Arguments:
        confId =graphene.String(required=True)
        pageId =graphene.String(required=True)
        auth =graphene.String(required=True)

    liked = graphene.Boolean()

    @staticmethod
    def mutate(root, info, confId, auth,pageId, input=None):
        page = Page.objects.get(pageId=pageId)
        pin=hashlib.sha256(str(page.pin).encode('utf-8')).hexdigest()
        if auth==pin:   
            confession_instance = Confession.objects.get(confId=confId)
            confession_instance.ownerLiked=not(confession_instance.ownerLiked)
            confession_instance.save()
            return AdminLikeConfession(liked=Confession.objects.get(confId=confId).ownerLiked)

class AdminPublicPage(graphene.Mutation):
    class Arguments:
        pageId =graphene.String(required=True)
        auth =graphene.String(required=True)

    isPublic = graphene.Boolean()

    @staticmethod
    def mutate(root, info, auth,pageId, input=None):
        page = Page.objects.get(pageId=pageId)
        pin=hashlib.sha256(str(page.pin).encode('utf-8')).hexdigest()
        if auth==pin:   
            page.isPublic = not(page.isPublic)
            page.save()
            return AdminPublicPage(isPublic=Page.objects.get(pageId=pageId).isPublic)
        
#REGISTER MUTATIONS

class Mutation(graphene.ObjectType):
    create_page = CreatePage.Field()
    delete_page = DeletePage.Field()
    create_confession = CreateConfession.Field()
    delete_confession = DeleteConfession.Field()
    like_confession = LikeConfession.Field()
    admin_like_confession = AdminLikeConfession.Field()
    admin_public_page = AdminPublicPage.Field()

