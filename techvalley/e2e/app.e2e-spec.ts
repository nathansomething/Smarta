import { TechvalleyPage } from './app.po';

describe('techvalley App', () => {
  let page: TechvalleyPage;

  beforeEach(() => {
    page = new TechvalleyPage();
  });

  it('should display message saying app works', () => {
    page.navigateTo();
    expect(page.getParagraphText()).toEqual('app works!');
  });
});
