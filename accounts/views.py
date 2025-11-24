from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    def form_valid(self, form):
        remember = self.request.POST.get('remember_me')
        response = super().form_valid(form)
        if remember:
            # two weeks
            self.request.session.set_expiry(1209600)
        else:
            # expire on browser close
            self.request.session.set_expiry(0)
        return response
